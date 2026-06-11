from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODE_RULES_PATH = ROOT / "runtime" / "mode_system" / "mode_rules.json"

OPERATING_MODES = {"creative_writing", "acf_lite"}
CREATIVE_DISABLED_VALIDATORS = {
    "insight_density_validator",
    "viral_integrity_validator",
    "platform_fit_validator",
    "hook_strength_validator",
    "identity_resonance_validator",
    "shareability_validator",
    "novelty_validator",
}
ACF_REQUIRED_FIELDS = (
    "claim",
    "defined_window",
    "external_collider",
    "uncertainty_sentence",
    "outcome_window",
)
METAPHOR_TERMS = {
    "lantern", "weather", "season", "river", "garden", "seed", "shore", "hearth", "fire", "root", "bone", "door"
}


def load_mode_rules() -> dict:
    return json.loads(MODE_RULES_PATH.read_text(encoding="utf-8"))


def resolve_operating_mode(profile: dict) -> str:
    requested = str(profile.get("mode", "") or "").strip().lower()
    creative = bool(profile.get("creative_writing_mode")) or requested == "creative_writing"
    acf = bool(profile.get("acf_lite_mode")) or requested == "acf_lite"
    rules = load_mode_rules()

    if rules["global_rules"]["mutual_exclusion"] and creative and acf:
        raise ValueError("Creative Writing and ACF Lite cannot be active at the same time.")
    if creative:
        return "creative_writing"
    if acf:
        return "acf_lite"
    if requested in OPERATING_MODES:
        return requested
    return "creative_writing"


def mode_contract(mode: str) -> dict:
    rules = load_mode_rules()
    if mode not in rules["mode_rules"]:
        raise KeyError(f"Unsupported operating mode: {mode}")
    return rules["mode_rules"][mode]


def canonical_generation_mode(mode: str) -> str:
    return "narrative" if mode == "creative_writing" else "authority"


def ui_visibility(mode: str) -> dict:
    if mode == "creative_writing":
        return {
            "show_fields": [
                "topic",
                "mode",
                "grit",
                "platform",
                "length",
                "voice_profile",
                "creative_pattern_controls",
                "human_texture_controls",
            ],
            "hide_fields": [
                "claim",
                "disconfirmation_window",
                "external_collider",
                "uncertainty_sentence",
                "outcome_window",
            ],
        }
    return {
        "show_fields": [
            "topic_or_claim",
            "defined_window",
            "external_collider",
            "uncertainty_sentence",
            "outcome_window",
            "model_controls",
        ],
        "hide_fields": [
            "creative_pattern_controls",
            "metaphor_heavy_controls",
            "human_texture_toggles",
        ],
    }


def apply_mode_to_profile(profile: dict) -> dict:
    operating_mode = resolve_operating_mode(profile)
    contract = mode_contract(operating_mode)
    updated = dict(profile)
    updated["mode"] = canonical_generation_mode(operating_mode)
    updated["selected_mode"] = operating_mode
    updated["mode_contract_applied"] = contract
    updated["creative_writing_mode"] = operating_mode == "creative_writing"
    updated["acf_lite_mode"] = operating_mode == "acf_lite"
    updated["acf_requirements_active"] = contract["acf_enabled"]
    updated["imagination_allowed"] = contract["imagination_allowed"]
    updated["human_texture_allowed"] = contract["human_texture_allowed"]
    return updated


def filter_validator_registry(profile: dict, validator_registry: dict) -> dict:
    operating_mode = resolve_operating_mode(profile)
    if operating_mode != "creative_writing":
        return validator_registry
    return {
        **validator_registry,
        "validators": [
            item for item in validator_registry["validators"]
            if item["validator_id"] not in CREATIVE_DISABLED_VALIDATORS
        ],
    }


def build_generation_guidance(profile: dict) -> dict:
    operating_mode = resolve_operating_mode(profile)
    contract = mode_contract(operating_mode)
    if operating_mode == "creative_writing":
        return {
            "selected_mode": operating_mode,
            "prompt_instruction": (
                "Use imaginative but human prose. Symbolic reasoning and metaphor are allowed. "
                "Do not flatten the language into claim-checking prose."
            ),
            "mode_violation_flags": [],
            "acf_requirements_active": False,
            "imagination_allowed": True,
            "human_texture_allowed": contract["human_texture_allowed"],
        }
    missing_fields = [field for field in ACF_REQUIRED_FIELDS if not str(profile.get(field, "") or "").strip()]
    flags = [f"missing_{field}" for field in missing_fields]
    return {
        "selected_mode": operating_mode,
        "prompt_instruction": (
            "Write in ACF Lite mode. Avoid invented scenes, symbolic leaps, or imagination-heavy language. "
            "Use strict claim framing, include a disconfirmation condition, external collider, uncertainty disclosure, and outcome window."
        ),
        "mode_violation_flags": flags,
        "acf_requirements_active": True,
        "imagination_allowed": False,
        "human_texture_allowed": False,
    }


def detect_imagination_drift(text: str) -> bool:
    words = {token.lower() for token in re.findall(r"[A-Za-z']+", text)}
    return bool(words & METAPHOR_TERMS)
