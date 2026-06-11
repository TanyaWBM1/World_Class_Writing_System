from __future__ import annotations

from runtime.phrase_system.phrase_runtime import phrase_analysis, clamp


def evaluate_grit_phrase_reuse(text: str, grit_level: str) -> dict:
    analysis = phrase_analysis(text, grit_level)
    score = clamp(1.0 - analysis["grit_phrase_reuse_risk"])
    status = "pass" if score >= 0.82 else "warn" if score >= 0.65 else "fail"
    return {
        "validator_id": "grit_phrase_reuse_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "grit_phrase_reuse_risk": analysis["grit_phrase_reuse_risk"],
            "grit_phrase_hits": analysis["grit_phrase_hits"],
            "phrase_diversity_score": analysis["phrase_diversity_score"]
        }
    }
