from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTENT_ENGINE_DIR = ROOT / "runtime" / "content_engine"
RUNS_DIR = ROOT / "runs"
APPROVAL_QUEUE_PATH = CONTENT_ENGINE_DIR / "approval_queue.json"
PUBLISH_MANIFEST_PATH = CONTENT_ENGINE_DIR / "publish_manifest.json"

from runtime.generation.llm_backend import run_llm_generation


VALID_APPROVAL_STATES = {"generated", "needs_review", "approved", "rejected"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "_" for char in value.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "topic"


def timestamp_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def platform_length(platform: str) -> str:
    if platform in {"linkedin", "reddit", "youtube"}:
        return "medium"
    return "short"


def initial_approval_state(final_status: str) -> str:
    return "generated" if final_status in {"accepted", "accepted_with_warnings"} else "needs_review"


def rank_output(evaluation_report: dict) -> dict:
    score_map = {
        "voice_alignment": evaluation_report.get("voice_alignment_score", 0.0),
        "lexical_alignment": evaluation_report.get("lexical_alignment_score", 0.0),
        "phrase_diversity": evaluation_report.get("phrase_diversity_score", 0.0),
        "reader_impact": evaluation_report.get("dimension_scores", {}).get("reader_impact", 0.0),
        "virality": evaluation_report.get("viral_score", 0.0),
        "platform_fit": evaluation_report.get("platform_fit_score", 0.0),
    }
    weighted_score = round(
        0.22 * score_map["voice_alignment"]
        + 0.18 * score_map["lexical_alignment"]
        + 0.14 * score_map["phrase_diversity"]
        + 0.18 * score_map["reader_impact"]
        + 0.14 * score_map["virality"]
        + 0.14 * score_map["platform_fit"],
        3,
    )
    return {
        "weighted_score": weighted_score,
        "score_breakdown": score_map,
    }


def ensure_registry_files() -> None:
    if not APPROVAL_QUEUE_PATH.exists():
        write_json(
            APPROVAL_QUEUE_PATH,
            {
                "queue_id": "content_engine_approval_queue_v1",
                "items": [],
                "last_updated": "",
            },
        )
    if not PUBLISH_MANIFEST_PATH.exists():
        write_json(
            PUBLISH_MANIFEST_PATH,
            {
                "manifest_id": "content_engine_publish_manifest_v1",
                "exports": [],
                "last_updated": "",
            },
        )


def build_content_plan(
    topics: list[str],
    mode: str,
    grit: str,
    voice_profile: str,
    platforms: list[str],
    output_count_per_topic: int,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    clean_topics = [topic.strip() for topic in topics if topic.strip()]
    return {
        "plan_id": timestamp_id("content_plan"),
        "topics": clean_topics,
        "selected_mode": mode,
        "selected_grit": grit,
        "selected_voice_profile": voice_profile,
        "selected_platforms": platforms,
        "desired_output_count_per_topic": output_count_per_topic,
        "llm_settings": {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    }


def queue_item_from_result(
    item_id: str,
    topic: str,
    variant_label: str,
    platform: str,
    output_index: int,
    run_dir: Path,
    result: dict,
) -> dict:
    evaluation_report = result.get("evaluation_report", {})
    ranking = rank_output(evaluation_report) if evaluation_report else {"weighted_score": 0.0, "score_breakdown": {}}
    final_status = result.get("run_summary", {}).get("final_status", result.get("final_status", "unknown"))
    return {
        "item_id": item_id,
        "topic": topic,
        "variant_label": variant_label,
        "platform": platform,
        "output_index": output_index,
        "approval_state": initial_approval_state(final_status),
        "final_status": final_status,
        "ranking": ranking,
        "run_dir": str(run_dir),
        "raw_output_path": str(run_dir / "raw_llm_output.txt"),
        "governed_output_path": str(run_dir / "final_governed_output.txt"),
        "evaluation_report_path": str(run_dir / "evaluation_report.json"),
        "enforcement_report_path": str(run_dir / "enforcement_report.json"),
        "run_summary_path": str(run_dir / "run_summary.json"),
    }


def generate_variant_settings(
    topic: str,
    mode: str,
    grit: str,
    voice_profile: str,
    platform: str,
    output_index: int,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    return {
        "run_id": f"{slugify(topic)}_{platform}_{output_index:02d}",
        "topic": topic,
        "mode": mode,
        "grit": grit,
        "platform": platform,
        "length": "long" if platform == "none" else platform_length(platform),
        "voice_profile": voice_profile,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def append_global_queue(batch_id: str, items: list[dict]) -> None:
    ensure_registry_files()
    queue = load_json(APPROVAL_QUEUE_PATH)
    queue["items"] = [item for item in queue.get("items", []) if item.get("batch_id") != batch_id] + [
        {**item, "batch_id": batch_id} for item in items
    ]
    queue["last_updated"] = datetime.now().isoformat()
    write_json(APPROVAL_QUEUE_PATH, queue)


def run_batch(
    content_plan: dict,
    transport=None,
    env_path: Path | None = None,
) -> dict:
    ensure_registry_files()
    batch_id = timestamp_id("content_engine_batch")
    batch_dir = RUNS_DIR / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    write_json(batch_dir / "content_plan.json", content_plan)

    queue_items: list[dict] = []
    batch_results: list[dict] = []
    model = content_plan["llm_settings"]["model"]
    temperature = content_plan["llm_settings"]["temperature"]
    max_tokens = content_plan["llm_settings"]["max_tokens"]

    for topic in content_plan["topics"]:
        topic_slug = slugify(topic)
        for output_index in range(1, content_plan["desired_output_count_per_topic"] + 1):
            base_dir = batch_dir / topic_slug / f"output_{output_index:02d}" / "base"
            base_settings = generate_variant_settings(
                topic,
                content_plan["selected_mode"],
                content_plan["selected_grit"],
                content_plan["selected_voice_profile"],
                "none",
                output_index,
                model,
                temperature,
                max_tokens,
            )
            base_result = run_llm_generation(
                base_settings,
                base_dir,
                transport=transport,
                run_full_validation=True,
                env_path=env_path,
            )
            base_item_id = f"{topic_slug}_base_{output_index:02d}"
            queue_items.append(queue_item_from_result(base_item_id, topic, "base_long_form", "none", output_index, base_dir, base_result))
            batch_results.append({"item_id": base_item_id, "result": base_result})

            for platform in content_plan["selected_platforms"]:
                variant_dir = batch_dir / topic_slug / f"output_{output_index:02d}" / platform
                variant_settings = generate_variant_settings(
                    topic,
                    content_plan["selected_mode"],
                    content_plan["selected_grit"],
                    content_plan["selected_voice_profile"],
                    platform,
                    output_index,
                    model,
                    temperature,
                    max_tokens,
                )
                variant_result = run_llm_generation(
                    variant_settings,
                    variant_dir,
                    transport=transport,
                    run_full_validation=True,
                    env_path=env_path,
                )
                item_id = f"{topic_slug}_{platform}_{output_index:02d}"
                queue_items.append(queue_item_from_result(item_id, topic, "platform_variant", platform, output_index, variant_dir, variant_result))
                batch_results.append({"item_id": item_id, "result": variant_result})

    approval_queue = {
        "queue_id": f"{batch_id}_approval_queue",
        "batch_id": batch_id,
        "items": sorted(queue_items, key=lambda item: item["ranking"]["weighted_score"], reverse=True),
        "last_updated": datetime.now().isoformat(),
    }
    write_json(batch_dir / "approval_queue.json", approval_queue)
    append_global_queue(batch_id, approval_queue["items"])

    publish_manifest = {
        "manifest_id": f"{batch_id}_publish_manifest",
        "batch_id": batch_id,
        "exports": [],
        "last_updated": datetime.now().isoformat(),
    }
    write_json(batch_dir / "publish_manifest.json", publish_manifest)

    summary = {
        "batch_id": batch_id,
        "batch_dir": str(batch_dir),
        "topic_count": len(content_plan["topics"]),
        "generated_item_count": len(queue_items),
        "top_ranked_items": [
            {
                "item_id": item["item_id"],
                "topic": item["topic"],
                "platform": item["platform"],
                "weighted_score": item["ranking"]["weighted_score"],
                "approval_state": item["approval_state"],
            }
            for item in approval_queue["items"][:10]
        ],
    }
    write_json(batch_dir / "batch_summary.json", summary)

    return {
        "batch_id": batch_id,
        "batch_dir": str(batch_dir),
        "approval_queue": approval_queue,
        "publish_manifest": publish_manifest,
        "batch_summary": summary,
    }


def load_batch_queue(batch_dir: Path) -> dict:
    return load_json(batch_dir / "approval_queue.json")


def save_batch_queue(batch_dir: Path, queue: dict) -> None:
    queue["last_updated"] = datetime.now().isoformat()
    write_json(batch_dir / "approval_queue.json", queue)
    append_global_queue(queue["batch_id"], queue["items"])


def update_approval_state(batch_dir: Path, item_id: str, new_state: str) -> dict:
    if new_state not in VALID_APPROVAL_STATES:
        raise ValueError(f"Unsupported approval state: {new_state}")

    queue = load_batch_queue(batch_dir)
    for item in queue["items"]:
        if item["item_id"] == item_id:
            item["approval_state"] = new_state
            save_batch_queue(batch_dir, queue)
            return item
    raise KeyError(f"Item not found: {item_id}")


def export_approved_bundle(batch_dir: Path) -> dict:
    queue = load_batch_queue(batch_dir)
    approved_items = [item for item in queue["items"] if item["approval_state"] == "approved"]
    export_id = timestamp_id("approved_bundle")
    export_dir = batch_dir / "exports" / export_id
    export_dir.mkdir(parents=True, exist_ok=True)

    for item in approved_items:
        source_dir = Path(item["run_dir"])
        target_dir = export_dir / "items" / item["item_id"]
        if source_dir.exists():
            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)

    bundle = {
        "bundle_id": export_id,
        "batch_id": queue["batch_id"],
        "approved_item_count": len(approved_items),
        "items": [
            {
                "item_id": item["item_id"],
                "topic": item["topic"],
                "platform": item["platform"],
                "approval_state": item["approval_state"],
                "weighted_score": item["ranking"]["weighted_score"],
            }
            for item in approved_items
        ],
        "export_dir": str(export_dir),
        "exported_at": datetime.now().isoformat(),
    }
    write_json(export_dir / "output_bundle.json", bundle)

    manifest = load_json(batch_dir / "publish_manifest.json")
    manifest["exports"].append(bundle)
    manifest["last_updated"] = datetime.now().isoformat()
    write_json(batch_dir / "publish_manifest.json", manifest)

    global_manifest = load_json(PUBLISH_MANIFEST_PATH)
    global_manifest["exports"].append(bundle)
    global_manifest["last_updated"] = datetime.now().isoformat()
    write_json(PUBLISH_MANIFEST_PATH, global_manifest)
    return bundle
