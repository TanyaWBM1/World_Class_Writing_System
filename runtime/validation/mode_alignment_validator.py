from __future__ import annotations

from typing import Any


def _classify_threshold(score: float) -> str:
    if score < 0.48:
        return "fail"
    if score < 0.72:
        return "warn"
    return "pass"


def evaluate_mode_alignment(mode_selection: dict, evaluation_report: dict) -> dict[str, Any]:
    dimension_scores = evaluation_report.get("dimension_scores", {})
    mode_id = mode_selection["mode_id"]

    dominant_requirements = {
        "utility": ["viral_intelligence", "reader_impact"],
        "narrative": ["reader_impact", "human_texture"],
        "authority": ["narrative_intelligence", "reader_impact"],
        "hybrid": ["reader_impact", "human_texture", "viral_intelligence"],
    }
    required_dimensions = dominant_requirements.get(mode_id, ["reader_impact"])
    available_scores = [dimension_scores.get(name, 0.0) for name in required_dimensions]
    score = round(sum(available_scores) / max(len(available_scores), 1), 3)

    evidence = {
        "mode_id": mode_id,
        "required_dimensions": required_dimensions,
        "dimension_scores_used": {name: dimension_scores.get(name, 0.0) for name in required_dimensions},
        "dominant_pillars": mode_selection.get("dominant_pillars", []),
        "selection_evidence": mode_selection.get("selection_evidence", {}),
    }
    return {
        "validator_id": "mode_alignment_validator",
        "score": score,
        "status": _classify_threshold(score),
        "primary_library": "evaluation_library",
        "secondary_libraries": ["voice_library", "benchmark_fixture_library"],
        "evidence": evidence,
    }
