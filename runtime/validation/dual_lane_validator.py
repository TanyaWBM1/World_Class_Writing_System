from __future__ import annotations

from typing import Any


def _classify_threshold(score: float) -> str:
    if score < 0.46:
        return "fail"
    if score < 0.7:
        return "warn"
    return "pass"


def evaluate_dual_lane(weighting_profile: dict, evaluation_report: dict) -> dict[str, Any]:
    scores = evaluation_report.get("dimension_scores", {})
    machine_lane_score = round(
        (
            scores.get("continuity", 0.0)
            + scores.get("human_texture", 0.0)
            + scores.get("viral_intelligence", 0.0)
        ) / 3.0,
        3,
    )
    human_lane_score = round(
        (
            scores.get("reader_impact", 0.0)
            + scores.get("human_texture", 0.0)
            + scores.get("human_likeness", 0.0)
        ) / 3.0,
        3,
    )
    lane_balance_delta = round(abs(machine_lane_score - human_lane_score), 3)
    score = round(max(0.0, ((machine_lane_score + human_lane_score) / 2.0) - lane_balance_delta * 0.35), 3)

    evidence = {
        "machine_lane_pillars": weighting_profile.get("dual_lane_profiles", {}).get("machine_lane", []),
        "human_lane_pillars": weighting_profile.get("dual_lane_profiles", {}).get("human_lane", []),
        "machine_lane_score": machine_lane_score,
        "human_lane_score": human_lane_score,
        "lane_balance_delta": lane_balance_delta,
    }
    return {
        "validator_id": "dual_lane_validator",
        "score": score,
        "status": _classify_threshold(score),
        "primary_library": "evaluation_library",
        "secondary_libraries": ["abstraction_control_library", "voice_library"],
        "evidence": evidence,
    }
