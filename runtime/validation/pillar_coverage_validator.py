from __future__ import annotations

from typing import Any


DIMENSION_MAP = {
    "SEO": "viral_intelligence",
    "GEO": "continuity",
    "AIO": "viral_intelligence",
    "SDO": "human_texture",
    "EEO": "reader_impact",
    "NLO": "human_likeness",
    "HEO": "viral_intelligence",
}


def _classify_threshold(score: float) -> str:
    if score < 0.5:
        return "fail"
    if score < 0.72:
        return "warn"
    return "pass"


def evaluate_pillar_coverage(mode_selection: dict, evaluation_report: dict) -> dict[str, Any]:
    weights = mode_selection["weighting_profile"]["weights"]
    dimension_scores = evaluation_report.get("dimension_scores", {})
    pillar_scores = {}
    weighted_sum = 0.0
    for pillar, weight in weights.items():
        dimension_name = DIMENSION_MAP[pillar]
        pillar_score = dimension_scores.get(dimension_name, 0.0)
        pillar_scores[pillar] = {
            "dimension": dimension_name,
            "weight": weight,
            "score": pillar_score,
        }
        weighted_sum += pillar_score * weight

    score = round(weighted_sum, 3)
    uncovered_pillars = [pillar for pillar, payload in pillar_scores.items() if payload["score"] < 0.45 and payload["weight"] >= 0.14]
    evidence = {
        "mode_id": mode_selection["mode_id"],
        "pillar_scores": pillar_scores,
        "uncovered_pillars": uncovered_pillars,
        "dominant_pillars": mode_selection.get("dominant_pillars", []),
    }
    return {
        "validator_id": "pillar_coverage_validator",
        "score": score,
        "status": _classify_threshold(score),
        "primary_library": "evaluation_library",
        "secondary_libraries": ["benchmark_fixture_library", "system_design_library"],
        "evidence": evidence,
    }
