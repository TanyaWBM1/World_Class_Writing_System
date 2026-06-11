from __future__ import annotations

from runtime.voice_system.voice_runtime import clamp


GRIT_FORCE = {
    "low": 0.25,
    "medium": 0.5,
    "high": 0.78,
    "extreme": 1.0,
}


def evaluate_grit_appropriateness(grit_context: dict, profile: dict) -> dict:
    grit_level = grit_context.get("grit_level", "medium")
    mode_id = grit_context.get("mode_id", profile.get("mode", "hybrid"))
    sensitive_topic = bool(profile.get("sensitive_topic", False))
    emotional_fragility = profile.get("emotional_fragility", "unknown")
    self_deception = bool(profile.get("self_deception_detected", False))
    clear_avoidance = bool(profile.get("clear_avoidance_detected", False))

    harshness_penalty = 0.0
    softness_penalty = 0.0
    mode_mismatch_penalty = 0.0
    heo_penalty = 0.0
    findings = []

    if grit_level in {"high", "extreme"} and (sensitive_topic or emotional_fragility == "high"):
        harshness_penalty += 0.45
        heo_penalty += 0.3
        findings.append("excessive_harshness_for_context")

    if grit_level == "low" and (self_deception or clear_avoidance):
        softness_penalty += 0.3
        findings.append("truth_diluted_by_low_grit")

    if grit_level == "extreme" and mode_id in {"utility", "commercial"}:
        mode_mismatch_penalty += 0.32
        findings.append("grit_exceeds_mode_envelope")

    if grit_level == "extreme" and not (self_deception or clear_avoidance):
        heo_penalty += 0.28
        findings.append("extreme_grit_without_earned_context")

    score = clamp(1.0 - harshness_penalty - softness_penalty - mode_mismatch_penalty - heo_penalty)
    status = "pass" if score >= 0.72 else "warn" if score >= 0.5 else "fail"
    return {
        "validator_id": "grit_appropriateness_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "grit_level": grit_level,
            "grit_force_score": GRIT_FORCE.get(grit_level, 0.5),
            "sensitive_topic": sensitive_topic,
            "emotional_fragility": emotional_fragility,
            "self_deception_detected": self_deception,
            "clear_avoidance_detected": clear_avoidance,
            "too_harsh_for_context": harshness_penalty > 0.0,
            "too_soft_for_truth": softness_penalty > 0.0,
            "mode_mismatch": mode_mismatch_penalty > 0.0,
            "heo_violation_risk": round(heo_penalty, 3),
            "selection_reason": grit_context.get("selection_reason", ""),
            "findings": findings,
        },
    }
