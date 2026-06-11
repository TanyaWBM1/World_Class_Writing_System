from __future__ import annotations

from runtime.voice_system.voice_runtime import analyze_voice_text, clamp, load_voice_profile


def evaluate_voice_consistency(text: str, mode_id: str) -> dict:
    profile = load_voice_profile()
    analysis = analyze_voice_text(text, mode_id)
    score = clamp(
        0.18 * (1.0 if analysis["paragraph_first"] else 0.0)
        + 0.18 * analysis["lived_grounding_score"]
        + 0.12 * analysis["cultural_spiritual_grounding_score"]
        + 0.12 * analysis["reflective_instruction_score"]
        + 0.1 * analysis["calm_certainty_score"]
        + 0.08 * analysis["rhythm_variation_score"]
        + 0.08 * analysis["cadence_naturalness_score"]
        + 0.08 * analysis["thought_visibility_score"]
        + 0.08 * (1.0 if analysis["mode_expression_match"] else 0.0)
        + 0.07 * (1.0 if analysis["grounded_emotional_tone"] else 0.0)
        + 0.05 * (1.0 if analysis["meaningful_metaphor"] else 0.0)
        - 0.18 * analysis["marketer_voice_risk"]
        - 0.16 * analysis["corporate_language_risk"]
        - 0.14 * analysis["generic_motivation_risk"]
    )
    hard_fail = (
        analysis["marketer_voice_risk"] > 0.0
        or analysis["corporate_language_risk"] > 0.0
        or analysis["generic_motivation_risk"] > 0.0
        or not analysis["paragraph_first"]
        or analysis["lived_grounding_score"] < 0.45
    )
    status = "pass" if score >= 0.7 and not hard_fail else "warn" if score >= 0.58 and not hard_fail else "fail"
    return {
        "validator_id": "voice_consistency_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "voice_id": profile["voice_id"],
            "mode_id": mode_id,
            "voice_alignment_score": round(score, 3),
            "marketer_voice_risk": analysis["marketer_voice_risk"],
            "corporate_language_risk": analysis["corporate_language_risk"],
            "generic_motivation_risk": analysis["generic_motivation_risk"],
            "lived_grounding_score": analysis["lived_grounding_score"],
            "cultural_spiritual_grounding_score": analysis["cultural_spiritual_grounding_score"],
            "cadence_naturalness_score": analysis["cadence_naturalness_score"],
            "compression_flags": analysis["compression_flags"],
            "thought_visibility_score": analysis["thought_visibility_score"],
            "summarization_flags": analysis["summarization_flags"],
            "signals_present": analysis["signals_present"],
            "signals_missing": analysis["signals_missing"]
        }
    }
