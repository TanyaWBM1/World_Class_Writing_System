from __future__ import annotations

from runtime.phrase_system.phrase_runtime import phrase_analysis, clamp


def evaluate_rhetorical_frame_repetition(text: str, grit_level: str) -> dict:
    analysis = phrase_analysis(text, grit_level)
    frame_overuse = sum(max(0, count - 1) for count in analysis["rhetorical_frame_hits"].values())
    opening_overuse = len(analysis["repeated_sentence_openings"])
    score = clamp(1.0 - frame_overuse * 0.25 - opening_overuse * 0.18)
    status = "pass" if score >= 0.78 else "warn" if score >= 0.6 else "fail"
    return {
        "validator_id": "rhetorical_frame_repetition_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "phrase_diversity_score": analysis["phrase_diversity_score"],
            "repeated_sentence_openings": analysis["repeated_sentence_openings"],
            "rhetorical_frame_hits": analysis["rhetorical_frame_hits"]
        }
    }
