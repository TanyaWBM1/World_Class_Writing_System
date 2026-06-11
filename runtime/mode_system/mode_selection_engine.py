from __future__ import annotations

import json
from pathlib import Path

from runtime.mode_system.mode_router import (
    apply_mode_to_profile,
    canonical_generation_mode,
    filter_validator_registry,
    load_mode_rules,
    resolve_operating_mode,
)

ROOT = Path(__file__).resolve().parents[2]
MODE_REGISTRY_PATH = ROOT / "runtime" / "mode_system" / "mode_registry.json"
WEIGHTING_PROFILES_PATH = ROOT / "runtime" / "pillar_weighting" / "weighting_profiles.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_mode_alias(requested_mode: str | None, registry: dict) -> str:
    if not requested_mode:
        return "hybrid"
    lowered = requested_mode.strip().lower()
    if lowered in {mode["mode_id"] for mode in registry["canonical_modes"]}:
        return lowered
    return registry.get("compatibility_aliases", {}).get(lowered, "hybrid")


def infer_mode_from_profile(profile: dict, registry: dict) -> str:
    operating_mode = resolve_operating_mode(profile)
    mode = resolve_mode_alias(canonical_generation_mode(operating_mode), registry)
    if mode != "hybrid":
        return mode
    intent = " ".join(
        str(value).lower()
        for key, value in profile.items()
        if key in {"desired_reader_impact", "desired_viral_profile", "audience", "genre", "prompt_brief"}
    )
    if any(token in intent for token in ["trust", "evidence", "authority", "prove", "research"]):
        return "authority"
    if any(token in intent for token in ["story", "memory", "resonance", "narrative", "emotion"]):
        return "narrative"
    if any(token in intent for token in ["faq", "tutorial", "steps", "guide", "definition"]):
        return "utility"
    return "hybrid"


def filter_validator_registry_for_profile(profile: dict, validator_registry: dict) -> dict:
    return filter_validator_registry(profile, validator_registry)


def select_mode(profile: dict) -> dict:
    registry = load_json(MODE_REGISTRY_PATH)
    profiles = load_json(WEIGHTING_PROFILES_PATH)
    routed_profile = apply_mode_to_profile(profile)
    runtime_mode = routed_profile["selected_mode"]
    mode_id = infer_mode_from_profile(routed_profile, registry)
    mode_def = next(item for item in registry["canonical_modes"] if item["mode_id"] == mode_id)
    weighting = profiles["profiles"][mode_id]
    return {
        "mode_id": mode_id,
        "runtime_mode": runtime_mode or mode_id,
        "display_name": mode_def["display_name"],
        "description": mode_def["description"],
        "dominant_pillars": mode_def["dominant_pillars"],
        "supporting_pillars": mode_def["supporting_pillars"],
        "minimal_pillars": mode_def["minimal_pillars"],
        "weighting_profile": weighting,
        "selection_evidence": {
          "requested_mode": profile.get("mode"),
          "runtime_mode": runtime_mode or mode_id,
          "resolved_mode": mode_id,
          "target_platform": profile.get("target_platform"),
          "audience": profile.get("audience", ""),
        },
    }


if __name__ == "__main__":
    sample_profile = {
        "mode": "hybrid",
        "genre": "essayistic_long_form_post",
        "audience": "general internet readers",
        "target_platform": "linkedin",
        "desired_reader_impact": "trust and memorability",
        "desired_viral_profile": "high-integrity"
    }
    print(json.dumps(select_mode(sample_profile), indent=2))
