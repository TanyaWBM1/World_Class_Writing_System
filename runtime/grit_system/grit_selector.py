from __future__ import annotations

import json
from pathlib import Path

from runtime.voice_system.voice_runtime import load_voice_profile


ROOT = Path(__file__).resolve().parents[2]
GRIT_COOLDOWN_PATH = ROOT / "runtime" / "grit_system" / "grit_phrase_cooldowns.json"

GRIT_ORDER = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "extreme": 3,
}

DEFAULT_GRIT_PHRASES = {
    "low": [
        "You might be avoiding something here, but it may be easier to see once the facts stop moving.",
        "Something in this may need gentler honesty before it becomes clear.",
    ],
    "medium": [
        "You are going in circles, and some part of you already knows why.",
        "This keeps returning because the truth has not been faced cleanly yet.",
    ],
    "high": [
        "That is not confusion. It is avoidance dressed up as uncertainty.",
        "Stop pretending this is complexity when it is refusal.",
    ],
    "extreme": [
        "That is fear pretending to be truth.",
        "You are lying to yourself and calling it discernment.",
    ],
}


def load_grit_phrase_cooldowns() -> dict:
    return json.loads(GRIT_COOLDOWN_PATH.read_text(encoding="utf-8"))


def clamp_grit_to_mode(grit_level: str, mode_id: str, voice_profile: dict | None = None) -> str:
    profile = voice_profile or load_voice_profile()
    max_by_mode = profile.get("grit_control", {}).get("max_level_by_mode", {})
    max_level = max_by_mode.get(mode_id, profile.get("grit_control", {}).get("default_level", "medium"))
    if GRIT_ORDER.get(grit_level, 1) <= GRIT_ORDER.get(max_level, 1):
        return grit_level
    return max_level


def determine_grit_level(context: dict, voice_profile: dict | None = None) -> tuple[str, str]:
    profile = voice_profile or load_voice_profile()
    default_level = profile.get("grit_control", {}).get("default_level", "medium")
    mode_id = context.get("mode", "hybrid")

    if context.get("emotional_fragility") == "high":
        selected = "low"
        reason = "high_fragility_requires_gentle_delivery"
    elif context.get("sensitive_topic", False):
        selected = "low"
        reason = "topic_sensitivity_reduces_force"
    elif context.get("self_deception_detected", False):
        selected = "high"
        reason = "self_deception_requires_sharper_truth"
    elif context.get("clear_avoidance_detected", False):
        selected = "high"
        reason = "avoidance_detected_requires_direct_callout"
    elif mode_id == "authority":
        selected = "medium"
        reason = "authority_prefers_controlled_force"
    else:
        selected = default_level
        reason = "default_voice_grit"

    return clamp_grit_to_mode(selected, mode_id, profile), reason


def phrase_penalty(
    phrase: str,
    recent_grit_phrases: list[str],
    recent_grit_phrase_counts: dict[str, int],
    current_draft_grit_phrases: list[str],
    cooldown_map: dict,
) -> tuple[float, dict]:
    phrase_key = phrase.lower()
    phrase_config = cooldown_map.get("phrases", {}).get(
        phrase_key,
        {"cooldown_penalty_weight": 0.25},
    )
    base_weight = float(phrase_config.get("cooldown_penalty_weight", 0.25))
    scope = cooldown_map.get(
        "scope_multipliers",
        {"same_paragraph": 1.0, "same_draft": 0.75, "previous_draft": 0.45},
    )

    prior_mentions = recent_grit_phrases.count(phrase_key)
    prior_count = int(recent_grit_phrase_counts.get(phrase_key, 0))
    current_mentions = current_draft_grit_phrases.count(phrase_key)

    penalty = 0.0
    if prior_mentions:
        penalty += base_weight * float(scope.get("previous_draft", 0.45))
    if prior_count:
        penalty += base_weight * 0.12 * prior_count
    if current_mentions:
        penalty += base_weight * float(scope.get("same_draft", 0.75))
    if phrase_key in current_draft_grit_phrases[-1:] if current_draft_grit_phrases else []:
        penalty += base_weight * float(scope.get("same_paragraph", 1.0))
    if recent_grit_phrases and phrase_key == recent_grit_phrases[-1]:
        penalty += base_weight * 0.9

    return round(penalty, 3), {
        "phrase": phrase,
        "prior_mentions": prior_mentions,
        "prior_count": prior_count,
        "current_draft_mentions": current_mentions,
        "cooldown_penalty_weight": base_weight,
        "penalty": round(penalty, 3),
    }


def choose_grit_phrase(context: dict, grit_level: str) -> tuple[str, dict]:
    cooldown_map = load_grit_phrase_cooldowns()
    recent_grit_phrases = [item.lower() for item in context.get("recent_grit_phrases", [])]
    recent_grit_phrase_counts = {
        str(key).lower(): int(value) for key, value in context.get("recent_grit_phrase_counts", {}).items()
    }
    current_draft_grit_phrases = [item.lower() for item in context.get("current_draft_grit_phrases", [])]
    candidates = cooldown_map.get("phrase_families", {}).get(grit_level, DEFAULT_GRIT_PHRASES.get(grit_level, []))
    scored = []
    cooled = []
    for phrase in candidates:
        penalty, evidence = phrase_penalty(
            phrase,
            recent_grit_phrases,
            recent_grit_phrase_counts,
            current_draft_grit_phrases,
            cooldown_map,
        )
        score = round(1.0 - penalty, 3)
        scored.append((score, phrase, evidence))
        if penalty > 0.0:
            cooled.append(evidence)

    best_score, best_phrase, best_evidence = sorted(
        scored,
        key=lambda item: (-item[0], item[1].lower())
    )[0]
    return best_phrase, {
        "grit_phrase_family": grit_level,
        "grit_phrase_candidates": [
            {
                "phrase": phrase,
                "selection_score": score,
                "cooldown_penalty": evidence["penalty"],
            }
            for score, phrase, evidence in sorted(scored, key=lambda item: (-item[0], item[1].lower()))
        ],
        "grit_cooldown_applied": bool(cooled),
        "cooled_down_phrases": cooled,
        "selected_phrase_score": best_score,
        "selected_phrase_penalty": best_evidence["penalty"],
    }


def select_grit(context: dict, voice_profile: dict | None = None) -> dict:
    profile = voice_profile or load_voice_profile()
    default_level = profile.get("grit_control", {}).get("default_level", "medium")
    mode_id = context.get("mode", "hybrid")
    requested = context.get("requested_grit_level")

    grit_level, reason = determine_grit_level(context, profile)
    if requested in profile.get("grit_control", {}).get("allowed_levels", []):
        grit_level = clamp_grit_to_mode(requested, mode_id, profile)
        reason = "requested_grit_level"

    selected_phrase, phrase_meta = choose_grit_phrase(context, grit_level)
    return {
        "grit_level": grit_level,
        "requested_grit_level": requested,
        "pre_clamp_grit_level": grit_level,
        "mode_id": mode_id,
        "selection_reason": reason,
        "max_allowed_for_mode": profile.get("grit_control", {}).get("max_level_by_mode", {}).get(mode_id, default_level),
        "selected_grit_phrase": selected_phrase,
        "grit_phrase_family": phrase_meta["grit_phrase_family"],
        "grit_cooldown_applied": phrase_meta["grit_cooldown_applied"],
        "cooled_down_phrases": phrase_meta["cooled_down_phrases"],
        "grit_phrase_candidates": phrase_meta["grit_phrase_candidates"],
        "selected_phrase_score": phrase_meta["selected_phrase_score"],
        "selected_phrase_penalty": phrase_meta["selected_phrase_penalty"],
        "recent_grit_phrases": context.get("recent_grit_phrases", []),
        "recent_grit_phrase_counts": context.get("recent_grit_phrase_counts", {}),
    }
