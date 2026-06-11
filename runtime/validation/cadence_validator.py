from __future__ import annotations

from runtime.voice_system.voice_runtime import analyze_cadence, clamp


def evaluate_cadence(text: str) -> dict:
    analysis = analyze_cadence(text)
    score = analysis["cadence_naturalness_score"]
    fail = (
        analysis["short_sentence_ratio"] > analysis["rules"]["max_short_sentence_ratio"]
        or analysis["avg_sentences_per_paragraph"] < analysis["rules"]["min_avg_sentences_per_paragraph"] * 0.55
        or analysis["excessive_line_breaks"]
    )
    warn = (
        analysis["uniform_length_flag"]
        or analysis["underdeveloped_ideas_flag"]
        or analysis["overly_clean_transitions"]
        or analysis["tension_presence_score"] < 0.55
    )
    status = "fail" if fail else "warn" if warn else "pass"
    return {
        "validator_id": "cadence_validator",
        "score": round(score, 3),
        "status": status,
        "primary_library": "cadence_library",
        "secondary_libraries": [
            "voice_library",
            "evaluation_library",
            "failure_mode_library"
        ],
        "evidence": {
            "cadence_naturalness_score": analysis["cadence_naturalness_score"],
            "development_depth_score": analysis["development_depth_score"],
            "compression_score": analysis["compression_score"],
            "compression_flags": analysis["compression_flags"],
            "roughness_score": analysis["roughness_score"],
            "over_polish_flags": analysis["over_polish_flags"],
            "tension_presence_score": analysis["tension_presence_score"],
            "short_sentence_ratio": analysis["short_sentence_ratio"],
            "avg_sentences_per_paragraph": analysis["avg_sentences_per_paragraph"],
            "uniform_length_flag": analysis["uniform_length_flag"],
            "underdeveloped_ideas_flag": analysis["underdeveloped_ideas_flag"],
            "excessive_line_breaks": analysis["excessive_line_breaks"],
            "overly_clean_transitions": analysis["overly_clean_transitions"]
        }
    }
