from __future__ import annotations

from runtime.phrase_system.phrase_runtime import phrase_analysis


def evaluate_phrase_repetition(text: str, grit_level: str) -> dict:
    analysis = phrase_analysis(text, grit_level)
    score = analysis["phrase_diversity_score"]
    status = "pass" if score >= 0.76 else "warn" if score >= 0.58 else "fail"
    return {
        "validator_id": "phrase_repetition_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "phrase_diversity_score": analysis["phrase_diversity_score"],
            "exact_repetition_count": analysis["exact_repetition_count"],
            "near_duplicate_phrase_count": analysis["near_duplicate_phrase_count"],
            "signature_phrase_overuse_flag": analysis["signature_phrase_overuse_flag"]
        }
    }
