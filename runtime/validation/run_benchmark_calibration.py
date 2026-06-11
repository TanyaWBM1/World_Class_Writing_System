from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.validation.validator_engine import evaluate_text
OUTPUT_DIR = ROOT / "runtime" / "validation"

PREVIOUS_THRESHOLDS = {
    "human_likeness_discriminator": {"pass_min": 0.75, "warn_min": 0.68, "fail_below": 0.68},
    "cadence_variance_checker": {"pass_min": 0.74, "warn_min": 0.66, "fail_below": 0.66},
    "abstraction_ratio_checker": {"pass_min": 0.72, "warn_min": 0.64, "fail_below": 0.64},
    "semantic_redundancy_detector": {"pass_min": 0.78, "warn_min": 0.70, "fail_below": 0.70},
    "continuity_consistency_checker": {"pass_min": 0.86, "warn_min": 0.75, "fail_below": 0.75, "critical_failure_cap": 0},
    "dialogue_realism_checker": {"pass_min": 0.74, "warn_min": 0.66, "fail_below": 0.66},
    "human_style_preference_validator": {"pass_min": 0.74, "warn_min": 0.67, "fail_below": 0.67},
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def targeted_gating(statuses: list[str]) -> str:
    if "fail" in statuses:
        return "rejected"
    if "warn" in statuses:
        return "accepted_with_warnings"
    return "accepted"


def main() -> None:
    benchmark_index = load_json(ROOT / "libraries" / "benchmark_fixture_library" / "benchmark_suite_index.json")
    validator_registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")
    base_input = load_json(ROOT / "runs" / "sample_run_001" / "input_bundle.json")

    suite_results = []
    per_validator = {}
    total_fixtures = 0
    matched_fixtures = 0

    for suite_meta in benchmark_index["suites"]:
        suite_path = ROOT / "libraries" / "benchmark_fixture_library" / "entries" / f"{suite_meta['suite_id']}.json"
        suite = load_json(suite_path)
        fixture_results = []

        for fixture in suite["fixtures"]:
            total_fixtures += 1
            text = fixture["text_under_test"].replace("\\n", "\n")
            evaluation = evaluate_text(text, base_input, thresholds, validator_registry)
            all_outputs = {
                item["validator_id"]: {
                    "score": item["score"],
                    "status": item["status"],
                    "dimension": item["dimension"],
                    "evidence": item["evidence"],
                }
                for item in evaluation["validator_results"]
            }
            targeted_outputs = {
                key: all_outputs[key]
                for key in fixture["validator_targets"]
                if key in all_outputs
            }
            actual_status_by_validator = {
                key: value["status"] for key, value in targeted_outputs.items()
            }
            actual_gating = targeted_gating(list(actual_status_by_validator.values()))
            validator_matches = {
                key: actual_status_by_validator.get(key) == expected
                for key, expected in fixture["expected_status_by_validator"].items()
            }
            fixture_match = all(validator_matches.values()) and actual_gating == fixture["expected_gating_outcome"]
            if fixture_match:
                matched_fixtures += 1

            fixture_result = {
                "fixture_id": fixture["fixture_id"],
                "title": fixture["title"],
                "task_type": fixture["task_type"],
                "expected_status_by_validator": fixture["expected_status_by_validator"],
                "actual_status_by_validator": actual_status_by_validator,
                "expected_gating_outcome": fixture["expected_gating_outcome"],
                "actual_gating_outcome": actual_gating,
                "validator_matches": validator_matches,
                "fixture_match": fixture_match,
                "expected_failure_modes": fixture.get("expected_failure_modes", []),
                "all_validator_outputs": all_outputs,
            }
            fixture_results.append(fixture_result)

            for validator_id, expected_status in fixture["expected_status_by_validator"].items():
                record = per_validator.setdefault(
                    validator_id,
                    {
                        "fixtures_seen": 0,
                        "matches": 0,
                        "false_positives": [],
                        "false_negatives": [],
                        "warn_band_hits": 0,
                        "fail_band_hits": 0,
                    },
                )
                actual_status = actual_status_by_validator.get(validator_id)
                record["fixtures_seen"] += 1
                if actual_status == expected_status:
                    record["matches"] += 1
                else:
                    expected_index = ["pass", "warn", "fail"].index(expected_status)
                    actual_index = ["pass", "warn", "fail"].index(actual_status)
                    issue = {
                        "fixture_id": fixture["fixture_id"],
                        "expected": expected_status,
                        "actual": actual_status,
                    }
                    if actual_index > expected_index:
                        record["false_positives"].append(issue)
                    else:
                        record["false_negatives"].append(issue)
                if actual_status == "warn":
                    record["warn_band_hits"] += 1
                elif actual_status == "fail":
                    record["fail_band_hits"] += 1

        suite_results.append(
            {
                "suite_id": suite["id"],
                "fixture_count": len(fixture_results),
                "matched_fixture_count": sum(1 for item in fixture_results if item["fixture_match"]),
                "fixtures": fixture_results,
            }
        )

    weak_validators = []
    over_sensitive_validators = []
    for validator_id, record in per_validator.items():
        accuracy = record["matches"] / max(1, record["fixtures_seen"])
        record["accuracy"] = round(accuracy, 3)
        if accuracy < 0.85:
            weak_validators.append(validator_id)
        if record["false_positives"]:
            over_sensitive_validators.append(validator_id)

    results_payload = {
        "benchmark_run_id": "validator_calibration_round_1",
        "suite_count": len(suite_results),
        "fixture_count": total_fixtures,
        "matched_fixture_count": matched_fixtures,
        "targeted_accuracy": round(matched_fixtures / max(1, total_fixtures), 3),
        "evaluation_scope": "targeted_validator_comparison_with_full_output_capture",
        "suite_results": suite_results,
        "validator_summary": per_validator,
        "weak_validators": weak_validators,
        "over_sensitive_validators": over_sensitive_validators,
    }
    write_json(OUTPUT_DIR / "benchmark_validation_results.json", results_payload)

    threshold_changes = {
        "change_set_id": "evaluation_threshold_calibration_round_1",
        "changes": [],
        "scoring_adjustments": [
            "dialogue parsing now extracts quoted utterances instead of relying on line breaks",
            "dialogue realism now rewards true narrative bridge beats and penalizes expository dialogue",
            "continuity consistency now uses token-level location overlap and contradiction markers",
            "human style preference now rewards paragraph-form prose without requiring multi-paragraph length",
            "semantic redundancy now distinguishes refrain-like repetition from silent semantic collapse",
        ],
    }
    for validator_id, before in PREVIOUS_THRESHOLDS.items():
        after = thresholds["validator_thresholds"][validator_id]
        changed_fields = {
            key: {"before": before.get(key), "after": after.get(key)}
            for key in after
            if before.get(key) != after.get(key)
        }
        if changed_fields:
            threshold_changes["changes"].append(
                {
                    "validator_id": validator_id,
                    "changed_fields": changed_fields,
                }
            )
    write_json(OUTPUT_DIR / "threshold_changes.json", threshold_changes)

    mis_lines = [
        "# Validator Misclassification Report",
        "",
        "## Final Status",
        "",
        f"- Targeted fixture accuracy: {matched_fixtures}/{total_fixtures}",
        f"- Remaining false positives: {sum(len(item['false_positives']) for item in per_validator.values())}",
        f"- Remaining false negatives: {sum(len(item['false_negatives']) for item in per_validator.values())}",
        "",
        "## Pre-Calibration Problem Areas",
        "",
        "- Cadence variance over-rejected warn fixtures because the fail floor sat too close to the warning band.",
        "- Dialogue realism undercounted utterances when multiple quoted lines appeared on one paragraph line.",
        "- Continuity consistency treated location anchoring too literally and missed partial context retention.",
        "- Human style preference penalized single-paragraph prose that should count as valid paragraph-first writing.",
        "- Semantic redundancy over-penalized refrain-like repetition and under-modeled semantic frame recurrence.",
        "",
        "## Final Misclassification Inventory",
        "",
    ]
    if matched_fixtures == total_fixtures:
        mis_lines.append("- No remaining targeted misclassifications after calibration.")
    else:
        for validator_id, record in per_validator.items():
            for issue in record["false_positives"]:
                mis_lines.append(f"- False positive: `{validator_id}` on `{issue['fixture_id']}` expected `{issue['expected']}` actual `{issue['actual']}`.")
            for issue in record["false_negatives"]:
                mis_lines.append(f"- False negative: `{validator_id}` on `{issue['fixture_id']}` expected `{issue['expected']}` actual `{issue['actual']}`.")
    (OUTPUT_DIR / "validator_misclassification_report.md").write_text("\n".join(mis_lines) + "\n", encoding="utf-8")

    summary_lines = [
        "# Calibration Summary",
        "",
        "## Coverage",
        "",
        f"- Indexed suites executed: {len(suite_results)}",
        f"- Fixtures executed: {total_fixtures}",
        f"- Targeted classification accuracy after calibration: {matched_fixtures}/{total_fixtures}",
        "",
        "## Threshold Calibration Outcome",
        "",
        "- Cadence fail floor was lowered so low-variance but non-collapsed prose lands in warning instead of rejection.",
        "- Abstraction thresholds now separate grounded warning cases from true abstract collapse cases.",
        "- Semantic redundancy fail floor now reserves rejection for stronger novelty collapse while keeping adversarial repetition visible.",
        "- Continuity warning and fail bands now reflect partial state retention versus hard contradiction.",
        "- Dialogue realism thresholds now match the corrected utterance parsing and bridge-aware scoring model.",
        "- Human style preference thresholds now accept strong single-paragraph prose while still rejecting list-shaped summaries.",
        "",
        "## Residual Risks",
        "",
        "- Benchmarks are evaluated against their targeted validators for gating to avoid unrelated validator contamination in family-specific fixtures.",
        "- Full multi-validator end-to-end benchmark gating remains a separate calibration problem once broader fixture coverage exists for cross-dimension interactions.",
    ]
    (OUTPUT_DIR / "calibration_summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
