from __future__ import annotations

from runtime.voice_system.voice_runtime import analyze_lexical_grounding, clamp, load_vocabulary_profile


def evaluate_lexical_grounding(text: str, mode_id: str, context: dict | None = None) -> dict:
    profile = load_vocabulary_profile()
    analysis = analyze_lexical_grounding(text, profile, context)
    score = clamp(
        0.72 * analysis["lexical_alignment_score"]
        + 0.1 * min(analysis["concrete_word_ratio"] / max(profile["thresholds"]["concrete_word_ratio_min"], 0.001), 1.0)
        - 0.12 * min(analysis["abstract_word_ratio"] / max(profile["thresholds"]["abstract_word_ratio_fail"], 0.001), 1.0)
        - 0.08 * float(analysis["tone_mismatch"])
    )
    hard_fail = (
        analysis["abstract_word_ratio"] >= profile["thresholds"]["abstract_word_ratio_fail"]
        or analysis["corporate_ai_term_count"] >= 3
        or bool(analysis["blocked_terms"])
    )
    status = "pass" if score >= 0.7 and not hard_fail else "warn" if score >= 0.55 and not hard_fail else "fail"
    return {
        "validator_id": "lexical_grounding_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "mode_id": mode_id,
            "lexical_alignment_score": analysis["lexical_alignment_score"],
            "abstract_word_ratio": analysis["abstract_word_ratio"],
            "concrete_word_ratio": analysis["concrete_word_ratio"],
            "flagged_terms": analysis["flagged_terms"],
            "blocked_terms": analysis["blocked_terms"],
            "corporate_ai_term_count": analysis["corporate_ai_term_count"],
            "everyday_language_tone_mismatch": analysis["tone_mismatch"]
        }
    }
