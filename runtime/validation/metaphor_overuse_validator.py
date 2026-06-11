from __future__ import annotations

from runtime.phrase_system.phrase_runtime import phrase_analysis, clamp


def evaluate_metaphor_overuse(text: str, grit_level: str) -> dict:
    analysis = phrase_analysis(text, grit_level)
    score = clamp(1.0 - analysis["metaphor_overuse_risk"])
    status = "pass" if score >= 0.8 else "warn" if score >= 0.62 else "fail"
    return {
        "validator_id": "metaphor_overuse_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "metaphor_overuse_risk": analysis["metaphor_overuse_risk"],
            "metaphor_domain_hits": analysis["metaphor_domain_hits"],
            "signature_phrase_overuse_flag": analysis["signature_phrase_overuse_flag"]
        }
    }
