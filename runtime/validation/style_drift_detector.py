from __future__ import annotations

from runtime.voice_system.voice_runtime import analyze_voice_text, clamp


def evaluate_style_drift(text: str, mode_id: str) -> dict:
    analysis = analyze_voice_text(text, mode_id)
    score = clamp(
        0.28 * (1.0 if analysis["paragraph_first"] else 0.0)
        + 0.22 * (1.0 if analysis["long_form_signal"] else 0.0)
        + 0.22 * analysis["rhythm_variation_score"]
        + 0.14 * (1.0 if analysis["mode_expression_match"] else 0.0)
        - 0.24 * analysis["list_overuse_risk"]
        - 0.16 * analysis["corporate_language_risk"]
    )
    detected_drifts = []
    if not analysis["paragraph_first"]:
        detected_drifts.append("paragraph_structure_loss")
    if analysis["list_overuse_risk"] >= 0.4:
        detected_drifts.append("list_overuse")
    if not analysis["mode_expression_match"]:
        detected_drifts.append("mode_expression_mismatch")
    if analysis["corporate_language_risk"] >= 0.34:
        detected_drifts.append("corporate_style_drift")
    status = "pass" if score >= 0.68 else "warn" if score >= 0.52 else "fail"
    return {
        "validator_id": "style_drift_detector",
        "score": round(score, 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "evaluation_library",
            "benchmark_fixture_library"
        ],
        "evidence": {
            "style_consistency_score": round(score, 3),
            "list_overuse_risk": analysis["list_overuse_risk"],
            "paragraph_first": analysis["paragraph_first"],
            "long_form_signal": analysis["long_form_signal"],
            "rhythm_variation_score": analysis["rhythm_variation_score"],
            "mode_expression_match": analysis["mode_expression_match"],
            "detected_drifts": detected_drifts
        }
    }
