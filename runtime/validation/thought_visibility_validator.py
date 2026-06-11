from __future__ import annotations

from runtime.voice_system.voice_runtime import analyze_thought_visibility


def evaluate_thought_visibility(text: str) -> dict:
    analysis = analyze_thought_visibility(text)
    fail = (
        analysis["early_conclusion_flag"]
        or analysis["missing_experiential_context"]
        or analysis["over_summarization_flag"]
    )
    warn = (
        analysis["clean_transition_bias"]
        or analysis["process_visibility_score"] < 0.58
        or analysis["tension_presence_score"] < 0.55
        or analysis["paragraph_end_summaries"] > 0
    )
    status = "fail" if fail else "warn" if warn else "pass"
    return {
        "validator_id": "thought_visibility_validator",
        "score": round(analysis["thought_visibility_score"], 3),
        "status": status,
        "primary_library": "voice_library",
        "secondary_libraries": [
            "cadence_library",
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "thought_visibility_score": analysis["thought_visibility_score"],
            "experiential_depth_score": analysis["experiential_depth_score"],
            "process_visibility_score": analysis["process_visibility_score"],
            "experience_presence_score": analysis["experience_presence_score"],
            "summarization_flags": analysis["summarization_flags"],
            "roughness_score": analysis["roughness_score"],
            "over_polish_flags": analysis["over_polish_flags"],
            "tension_presence_score": analysis["tension_presence_score"],
            "early_conclusion_flag": analysis["early_conclusion_flag"],
            "missing_experiential_context": analysis["missing_experiential_context"],
            "clean_transition_bias": analysis["clean_transition_bias"],
            "paragraph_end_summaries": analysis["paragraph_end_summaries"]
        }
    }
