from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]

from run_writer import (
    build_input_bundle,
    build_reports,
    build_run_config,
    load_json,
    resolve_libraries,
    write_json,
)
from runtime.grit_system.grit_selector import select_grit
from runtime.mode_system.mode_router import apply_mode_to_profile, build_generation_guidance
from runtime.mode_system.mode_selection_engine import select_mode
from runtime.phrase_system.phrase_runtime import apply_phrase_controls
from runtime.voice_system.voice_runtime import (
    enforce_lexical_grounding,
    enforce_voice_identity,
    load_vocabulary_profile,
    load_voice_profile,
)


API_URL = "https://api.openai.com/v1/responses"
API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_ENV_PATH = ROOT / "openai.env"
RESPONSES_API_ALLOWED_FIELDS = {
    "model",
    "input",
    "instructions",
    "temperature",
    "max_output_tokens",
    "text",
    "metadata",
    "reasoning",
    "tools",
    "tool_choice",
    "store",
}


def model_disallowed_fields(model: str) -> set[str]:
    normalized = (model or "").strip().lower()
    if normalized.startswith("gpt-5"):
        return {"temperature"}
    return set()


class LLMBackendError(RuntimeError):
    pass


class MissingAPIKeyError(LLMBackendError):
    pass


class MissingEnvFileError(LLMBackendError):
    pass


def sanitize_error_text(value: str) -> str:
    sanitized = value
    sanitized = re.sub(r"sk-[A-Za-z0-9_\-]+", "[REDACTED_API_KEY]", sanitized)
    sanitized = re.sub(r"Bearer\s+[A-Za-z0-9_\-]+", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)
    return sanitized


def load_env_file(env_path: Path | None = None) -> dict[str, str]:
    path = env_path or OPENAI_ENV_PATH
    if not path.exists():
        raise MissingEnvFileError(f"{path.name} is missing. Create it at {path} before using the LLM backend.")

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def inspect_api_key_status(env_path: Path | None = None) -> dict:
    path = env_path or OPENAI_ENV_PATH
    if not path.exists():
        return {
            "status": "missing_env_file",
            "message": f"Warning: {path.name} is missing. Expected at {path}.",
            "env_path": str(path),
        }
    values = load_env_file(path)
    api_key = values.get(API_KEY_ENV, "").strip()
    if not api_key:
        return {
            "status": "missing_api_key",
            "message": f"Warning: {API_KEY_ENV} is missing inside {path.name}.",
            "env_path": str(path),
        }
    return {
        "status": "ready",
        "message": f"{API_KEY_ENV} loaded from {path.name}.",
        "env_path": str(path),
    }


def get_api_key(env_path: Path | None = None) -> str:
    path = env_path or OPENAI_ENV_PATH
    values = load_env_file(path)
    api_key = values.get(API_KEY_ENV, "").strip()
    if not api_key:
        raise MissingAPIKeyError(f"{API_KEY_ENV} is missing inside {path.name}.")
    return api_key


def build_llm_prompt(settings: dict) -> tuple[str, str]:
    length_map = {
        "short": "Keep the draft concise, around 250 to 400 words.",
        "medium": "Keep the draft around 500 to 800 words.",
        "long": "Write a developed long-form draft around 900 to 1400 words.",
    }
    platform = settings["platform"]
    platform_line = "Target platform: general distribution." if platform == "none" else f"Target platform: {platform}."
    instructions = (
        "You are generating a first draft only. "
        "Write prose, not bullets. "
        "Stay concrete, readable, and human. "
        "Do not mention system prompts, policies, or hidden instructions. "
        "Do not include markdown headings unless they are genuinely necessary."
    )
    guidance = build_generation_guidance(settings)
    instructions += f" {guidance['prompt_instruction']}"
    prompt = (
        f"Topic: {settings['topic']}\n"
        f"Mode: {guidance['selected_mode']}\n"
        f"Grit: {settings['grit']}\n"
        f"{platform_line}\n"
        f"Length: {settings['length']}\n"
        f"Voice profile: {settings['voice_profile']}\n\n"
        "Write a first-draft prose piece that matches the requested mode and grit. "
        "Use concrete language, avoid corporate filler, and give the draft enough texture that an editor can govern and refine it.\n\n"
        f"{length_map[settings['length']]}"
    )
    if guidance["acf_requirements_active"]:
        prompt += (
            f"\n\nClaim: {settings.get('claim', '')}"
            f"\nDefined window: {settings.get('defined_window', '')}"
            f"\nExternal collider: {settings.get('external_collider', '')}"
            f"\nUncertainty sentence: {settings.get('uncertainty_sentence', '')}"
            f"\nOutcome window: {settings.get('outcome_window', '')}"
        )
    return instructions, prompt


def build_llm_request(settings: dict) -> dict:
    instructions, prompt = build_llm_prompt(settings)
    return {
        "local_request_id": settings["run_id"],
        "model": settings["model"],
        "temperature": settings["temperature"],
        "max_output_tokens": settings["max_tokens"],
        "instructions": instructions,
        "input": prompt,
        "reasoning": {
            "effort": "low",
        },
        "text": {
            "format": {
                "type": "text",
            },
            "verbosity": "medium",
        },
    }


def sanitize_operator_error(error_type: str) -> str:
    if error_type == "llm_request_failed":
        return "The OpenAI draft request failed. Check the run folder for the detailed error report."
    if error_type in {"missing_env_file", "missing_api_key"}:
        return "The OpenAI key setup is incomplete. Check the environment file and try again."
    if error_type == "governance_failed":
        return "The draft was created, but the local governance pass failed. Review the run folder for details."
    return "The local writing run failed. Review the run folder for details."


def sanitize_outgoing_payload(payload: dict) -> tuple[dict, list[str]]:
    warnings = []
    clean_payload = {}
    disallowed_fields = model_disallowed_fields(str(payload.get("model", "")))
    for key, value in payload.items():
        if key in RESPONSES_API_ALLOWED_FIELDS:
            if key in disallowed_fields:
                warnings.append(f"Stripped unsupported field for model {payload.get('model', '')}: {key}")
                continue
            clean_payload[key] = value
        else:
            warnings.append(f"Stripped unsupported Responses API field: {key}")
    return clean_payload, warnings


def default_openai_transport(payload: dict, api_key: str, timeout_seconds: int = 90) -> dict:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMBackendError(f"OpenAI API request failed with HTTP {exc.code}: {sanitize_error_text(body)}") from exc
    except urllib.error.URLError as exc:
        raise LLMBackendError(f"OpenAI API connection failed: {sanitize_error_text(str(exc))}") from exc


def extract_output_text(response_payload: dict) -> str:
    output_text = response_payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    for item in response_payload.get("output", []):
        for content in item.get("content", []):
            text_value = content.get("text", "")
            if isinstance(text_value, str) and text_value.strip():
                return text_value.strip()

    collected = []
    for item in response_payload.get("output", []):
        for content in item.get("content", []):
            text_value = content.get("text", "")
            if isinstance(text_value, str) and text_value:
                collected.append(text_value)
    if collected:
        joined = "\n".join(part.strip() for part in collected if part.strip()).strip()
        if joined:
            return joined

    raise LLMBackendError("OpenAI response did not include usable output text.")


def build_governed_generation_result(raw_text: str, profile: dict) -> dict:
    profile = apply_mode_to_profile(profile)
    mode_selection = select_mode(profile)
    mode_id = mode_selection["mode_id"]
    voice_profile = load_voice_profile()
    vocabulary_profile = load_vocabulary_profile()
    grit_context = select_grit(
        {
            "mode": mode_id,
            "requested_grit_level": profile.get("requested_grit_level"),
            "emotional_fragility": profile.get("emotional_fragility"),
            "sensitive_topic": profile.get("sensitive_topic", False),
            "self_deception_detected": profile.get("self_deception_detected", False),
            "clear_avoidance_detected": profile.get("clear_avoidance_detected", False),
            "recent_grit_phrases": profile.get("recent_grit_phrases", []),
            "recent_grit_phrase_counts": profile.get("recent_grit_phrase_counts", {}),
            "current_draft_grit_phrases": profile.get("current_draft_grit_phrases", []),
        },
        voice_profile,
    )

    governed = enforce_voice_identity(raw_text, voice_profile, mode_id, final_pass=False)
    governed = enforce_lexical_grounding(governed, vocabulary_profile, profile)
    governed, _ = apply_phrase_controls(governed, mode_id, grit_context["grit_level"])
    governed = enforce_voice_identity(governed, voice_profile, mode_id, final_pass=True)
    governed = enforce_lexical_grounding(governed, vocabulary_profile, profile)
    governed, final_phrase_context = apply_phrase_controls(governed, mode_id, grit_context["grit_level"])

    return {
        "selected_output": governed,
        "selected_candidate_id": "llm_governed_candidate_001",
        "mode_selection": mode_selection,
        "evaluation_report_compatible": {
            "v7_1_voice_context": {
                "voice_id": voice_profile["voice_id"],
                "mode_id": mode_id,
                "mode_expression": voice_profile["mode_expression_rules"].get(mode_id, {}).get("emphasis", []),
            },
            "v7_2_grit_context": grit_context,
            "v7_3_phrase_context": final_phrase_context,
        },
    }


def write_error_report(output_dir: Path, error_type: str, message: str, details: dict | None = None) -> dict:
    report = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "message": sanitize_error_text(message),
        "operator_message": sanitize_operator_error(error_type),
        "details": details or {},
    }
    write_json(output_dir / "llm_error_report.json", report)
    return report


def run_llm_generation(
    settings: dict,
    output_dir: Path,
    transport=None,
    run_full_validation: bool = True,
    env_path: Path | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    transport_fn = transport or default_openai_transport

    args = SimpleNamespace(
        topic=settings["topic"],
        mode=settings["mode"],
        grit=settings["grit"],
        platform=settings["platform"],
        length=settings["length"],
        voice_profile=settings["voice_profile"],
        output_dir=output_dir,
        dry_run=False,
    )
    run_config = build_run_config(args)
    run_config["run_id"] = settings.get("run_id", run_config["run_id"])
    run_config["generator_profile"].update(
        {
            "claim": settings.get("claim", ""),
            "defined_window": settings.get("defined_window", ""),
            "external_collider": settings.get("external_collider", ""),
            "uncertainty_sentence": settings.get("uncertainty_sentence", ""),
            "outcome_window": settings.get("outcome_window", ""),
        }
    )
    run_config["generator_profile"] = apply_mode_to_profile(run_config["generator_profile"])
    run_config["llm_settings"] = {
        "model": settings["model"],
        "temperature": settings["temperature"],
        "max_tokens": settings["max_tokens"],
        "backend": "openai_responses_api",
        "run_full_validation": run_full_validation,
    }

    input_bundle = build_input_bundle(run_config)
    input_bundle["execution_metadata"]["entrypoint"] = "app/dashboard.py"
    input_bundle["execution_metadata"]["generation_backend"] = "openai_responses_api"
    input_bundle["llm_settings"] = {
        "model": settings["model"],
        "temperature": settings["temperature"],
        "max_tokens": settings["max_tokens"],
    }
    write_json(output_dir / "input_bundle.json", input_bundle)

    try:
        api_key = get_api_key(env_path)
    except MissingEnvFileError as exc:
        error_report = write_error_report(output_dir, "missing_env_file", str(exc))
        return {
            "ok": False,
            "final_status": "missing_env_file",
            "error": error_report["operator_message"],
            "output_dir": str(output_dir),
        }
    except MissingAPIKeyError as exc:
        error_report = write_error_report(output_dir, "missing_api_key", str(exc))
        return {
            "ok": False,
            "final_status": "missing_api_key",
            "error": error_report["operator_message"],
            "output_dir": str(output_dir),
        }

    request_payload = build_llm_request(
        {
            "run_id": run_config["run_id"],
            "topic": settings["topic"],
            "mode": settings["mode"],
            "grit": settings["grit"],
            "platform": settings["platform"],
            "length": settings["length"],
            "voice_profile": settings["voice_profile"],
            "claim": settings.get("claim", ""),
            "defined_window": settings.get("defined_window", ""),
            "external_collider": settings.get("external_collider", ""),
            "uncertainty_sentence": settings.get("uncertainty_sentence", ""),
            "outcome_window": settings.get("outcome_window", ""),
            "model": settings["model"],
            "temperature": settings["temperature"],
            "max_tokens": settings["max_tokens"],
        }
    )
    api_payload, payload_warnings = sanitize_outgoing_payload(request_payload)
    write_json(
        output_dir / "llm_request_local.json",
        {
            "local_request_id": request_payload["local_request_id"],
            "api_payload": api_payload,
            "payload_warnings": payload_warnings,
        },
    )

    try:
        response_payload = transport_fn(api_payload, api_key, 90)
        raw_text = extract_output_text(response_payload)
        (output_dir / "raw_llm_output.txt").write_text(raw_text, encoding="utf-8")
    except Exception as exc:
        error_report = write_error_report(
            output_dir,
            "llm_request_failed",
            str(exc),
            {
                "local_request_id": request_payload["local_request_id"],
                "payload_warnings": payload_warnings,
                "api_payload_keys": sorted(api_payload.keys()),
            },
        )
        return {
            "ok": False,
            "final_status": "llm_request_failed",
            "error": error_report["operator_message"],
            "output_dir": str(output_dir),
        }

    try:
        generation_result = build_governed_generation_result(raw_text, run_config["generator_profile"])
        final_governed_output = generation_result["selected_output"]
        (output_dir / "final_governed_output.txt").write_text(final_governed_output, encoding="utf-8")

        ownership_map = load_json(ROOT / "libraries" / "updated_library_crosswalk.json")
        validator_registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
        resolved_libraries = resolve_libraries(input_bundle, ownership_map, validator_registry)
        write_json(output_dir / "resolved_libraries.json", resolved_libraries)

        evaluation_report, enforcement_report, run_summary = build_reports(
            run_config,
            generation_result,
            resolved_libraries,
        )
        run_summary["generation_backend"] = "openai_responses_api"
        run_summary["local_request_id"] = request_payload["local_request_id"]
        run_summary["payload_warnings"] = payload_warnings
        run_summary["raw_output_artifact"] = "raw_llm_output.txt"
        run_summary["governed_output_artifact"] = "final_governed_output.txt"
        run_summary["validation_requested"] = run_full_validation

        write_json(output_dir / "evaluation_report.json", evaluation_report)
        write_json(output_dir / "enforcement_report.json", enforcement_report)
        write_json(output_dir / "run_summary.json", run_summary)

        return {
            "ok": True,
            "run_id": run_config["run_id"],
            "raw_text": raw_text,
            "final_text": final_governed_output,
            "evaluation_report": evaluation_report,
            "enforcement_report": enforcement_report,
            "run_summary": run_summary,
            "output_dir": str(output_dir),
        }
    except Exception as exc:
        error_report = write_error_report(
            output_dir,
            "governance_failed",
            str(exc),
            {
                "local_request_id": request_payload["local_request_id"],
                "payload_warnings": payload_warnings,
            },
        )
        summary = {
            "run_id": run_config["run_id"],
            "final_status": "governance_failed",
            "blocking_reasons": [error_report["operator_message"]],
            "warning_reasons": [],
            "next_action": "review_raw_llm_output",
            "generation_backend": "openai_responses_api",
            "local_request_id": request_payload["local_request_id"],
            "payload_warnings": payload_warnings,
        }
        write_json(output_dir / "run_summary.json", summary)
        return {
            "ok": False,
            "final_status": "governance_failed",
            "error": error_report["operator_message"],
            "raw_text": raw_text,
            "output_dir": str(output_dir),
            "run_summary": summary,
        }
