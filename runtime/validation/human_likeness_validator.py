from __future__ import annotations

from runtime.voice_system.voice_runtime import analyze_voice_text, clamp


def evaluate_human_likeness(text: str, mode_id: str) -> dict:
    analysis = analyze_voice_text(text, mode_id)
    score = clamp(
        0.24 * analysis["lived_grounding_score"]
        + 0.16 * analysis["reflective_instruction_score"]
        + 0.16 * analysis["calm_certainty_score"]
        + 0.14 * analysis["rhythm_variation_score"]
        + 0.12 * (1.0 if analysis["grounded_emotional_tone"] else 0.0)
        + 0.1 * (1.0 if analysis["direct_thoughtful_phrasing"] else 0.0)
        + 0.06 * analysis["cultural_spiritual_grounding_score"]
        - 0.18 * analysis["marketer_voice_risk"]
        - 0.14 * analysis["corporate_language_risk"]
        - 0.12 * analysis["generic_motivation_risk"]
        - 0.1 * analysis["polished_empty_prose_risk"]
    )
    status = "pass" if score >= 0.64 else "warn" if score >= 0.5 else "fail"
    return {
        "validator_id": "human_likeness_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "human_likeness_score": round(score, 3),
            "marketer_voice_risk": analysis["marketer_voice_risk"],
            "corporate_language_risk": analysis["corporate_language_risk"],
            "generic_motivation_risk": analysis["generic_motivation_risk"],
            "lived_grounding_score": analysis["lived_grounding_score"],
            "cultural_spiritual_grounding_score": analysis["cultural_spiritual_grounding_score"],
            "polished_empty_prose_risk": analysis["polished_empty_prose_risk"],
            "calm_certainty_score": analysis["calm_certainty_score"],
            "reflective_instruction_score": analysis["reflective_instruction_score"]
        }
    }
