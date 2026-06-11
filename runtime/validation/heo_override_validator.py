from __future__ import annotations

from typing import Any


def evaluate_heo_override(evaluation_report: dict) -> dict[str, Any]:
    validator_results = {item["validator_id"]: item for item in evaluation_report.get("validator_results", [])}
    blocking_failures = list(evaluation_report.get("blocking_failures", []))

    viral_integrity = validator_results.get("viral_integrity_validator", {})
    insight_density = validator_results.get("insight_density_validator", {})
    manipulation_risk = viral_integrity.get("evidence", {}).get("manipulation_risk", 0.0)
    clickbait_risk = viral_integrity.get("evidence", {}).get("clickbait_risk", 0.0)
    generic_motivation = insight_density.get("evidence", {}).get("generic_motivation_detected", False)
    empty_insight = insight_density.get("evidence", {}).get("empty_insight_detected", False)

    override_triggered = (
        manipulation_risk >= 0.42
        or clickbait_risk >= 0.38
        or generic_motivation
        or (empty_insight and viral_integrity.get("score", 0.0) < 0.76)
    )
    score = 0.0 if override_triggered else 1.0
    status = "fail" if override_triggered else "pass"
    evidence = {
        "override_triggered": override_triggered,
        "manipulation_risk": manipulation_risk,
        "clickbait_risk": clickbait_risk,
        "generic_motivation_detected": generic_motivation,
        "empty_insight_detected": empty_insight,
        "blocking_failures_present": bool(blocking_failures),
        "override_reason": (
            "ethical override due to manipulation, clickbait, or shallow optimization"
            if override_triggered
            else "no HEO override conditions met"
        ),
    }
    return {
        "validator_id": "heo_override_validator",
        "score": score,
        "status": status,
        "primary_library": "evaluation_library",
        "secondary_libraries": ["failure_mode_library", "benchmark_fixture_library"],
        "evidence": evidence,
    }
