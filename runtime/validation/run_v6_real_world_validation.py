from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.validation.validator_engine import evaluate_text


PACK_PATH = ROOT / "runtime" / "validation" / "v6_real_world_validation_pack.json"
REPORT_PATH = ROOT / "runtime" / "validation" / "v6_real_world_validation_report.md"
CONFUSION_PATH = ROOT / "runtime" / "validation" / "v6_real_world_confusion_matrix.json"
FAILURE_PATH = ROOT / "runtime" / "validation" / "v6_real_world_failure_modes.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def favored_status(final_status: str) -> bool:
    return final_status in {"accepted", "accepted_with_warnings"}


def main() -> None:
    pack = load_json(PACK_PATH)
    registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")

    tp = tn = fp = fn = 0
    per_category: dict[str, dict] = {}
    fixture_results = []
    insight_changed_cases = []

    for fixture in pack["fixtures"]:
        result = evaluate_text(fixture["text_under_test"], {}, thresholds, registry)
        validators = {item["validator_id"]: item for item in result["validator_results"]}
        viral = result["reader_metrics"]["viral_metrics"]

        expected_favored = fixture["expected_favored"]
        actual_favored = favored_status(result["final_status"])

        if expected_favored and actual_favored:
            tp += 1
        elif not expected_favored and not actual_favored:
            tn += 1
        elif not expected_favored and actual_favored:
            fp += 1
        else:
            fn += 1

        category_bucket = per_category.setdefault(
            fixture["category"],
            {
                "fixture_count": 0,
                "expected_favored_count": 0,
                "actual_favored_count": 0,
                "false_positives": 0,
                "false_negatives": 0,
            },
        )
        category_bucket["fixture_count"] += 1
        category_bucket["expected_favored_count"] += int(expected_favored)
        category_bucket["actual_favored_count"] += int(actual_favored)
        if not expected_favored and actual_favored:
            category_bucket["false_positives"] += 1
        elif expected_favored and not actual_favored:
            category_bucket["false_negatives"] += 1

        insight_contributed = (
            validators["insight_density_validator"]["status"] == "fail"
            and validators["viral_integrity_validator"]["status"] == "pass"
        )
        if insight_contributed:
            insight_changed_cases.append(
                {
                    "fixture_id": fixture["fixture_id"],
                    "category": fixture["category"],
                    "title": fixture["title"],
                    "final_status": result["final_status"],
                    "insight_density_score": viral["insight_density_score"],
                    "generic_motivation_detected": viral["generic_motivation_detected"],
                    "empty_insight_detected": viral["empty_insight_detected"],
                    "shallow_philosophy_detected": viral["shallow_philosophy_detected"],
                }
            )

        fixture_results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "category": fixture["category"],
                "title": fixture["title"],
                "expected_favored": expected_favored,
                "expected_gating_outcome": fixture["expected_gating_outcome"],
                "actual_favored": actual_favored,
                "actual_gating_outcome": result["final_status"],
                "validator_statuses": {
                    "HighArousalEmotionValidator": validators["high_arousal_emotion_validator"]["status"],
                    "HookStrengthValidator": validators["hook_strength_validator"]["status"],
                    "IdentityResonanceValidator": validators["identity_resonance_validator"]["status"],
                    "ShareabilityValidator": validators["shareability_validator"]["status"],
                    "NoveltyValidator": validators["novelty_validator"]["status"],
                    "InsightDensityValidator": validators["insight_density_validator"]["status"],
                    "ViralIntegrityValidator": validators["viral_integrity_validator"]["status"],
                },
                "scores": {
                    "high_arousal_score": viral["high_arousal_score"],
                    "hook_strength_score": viral["hook_strength_score"],
                    "identity_resonance_score": viral["identity_resonance_score"],
                    "shareability_score": viral["shareability_score"],
                    "novelty_score": viral["novelty_score"],
                    "insight_density_score": viral["insight_density_score"],
                    "viral_integrity_score": viral["viral_integrity_score"],
                    "viral_score": viral["viral_score"],
                },
                "signals": {
                    "high_integrity_viral_cases": viral["high_integrity_viral_cases"],
                    "generic_motivation_detected": viral["generic_motivation_detected"],
                    "empty_insight_detected": viral["empty_insight_detected"],
                    "shallow_philosophy_detected": viral["shallow_philosophy_detected"],
                    "hook_content_mismatch": viral["hook_content_mismatch"],
                    "emotional_manipulation_without_payoff": viral["emotional_manipulation_without_payoff"],
                    "identity_bait_without_substance": viral["identity_bait_without_substance"],
                    "shallow_virality": viral["shallow_virality"],
                },
                "insight_contributed_to_rejection": insight_contributed and result["final_status"] == "rejected",
            }
        )

    favored_high_integrity = sum(
        1 for item in fixture_results
        if item["category"] == "high_integrity_viral" and item["actual_favored"]
    )
    favored_shallow = sum(
        1 for item in fixture_results
        if item["category"] in {"generic_viral_looking", "manipulative_clickbait", "outrage_bait"} and item["actual_favored"]
    )

    confusion_payload = {
        "suite_id": pack["suite_id"],
        "positive_class_definition": "content expected to be favored by the current v6/v6.1 system",
        "overall": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "total_fixtures": len(pack["fixtures"]),
        },
        "per_category": per_category,
        "high_integrity_vs_shallow": {
            "high_integrity_favored_count": favored_high_integrity,
            "shallow_favored_count": favored_shallow,
            "high_integrity_favored_over_shallow": favored_high_integrity > favored_shallow,
        },
        "insight_density_changed_outcomes": insight_changed_cases,
        "fixture_results": fixture_results,
    }
    write_json(CONFUSION_PATH, confusion_payload)

    report_lines = [
        "# V6 Real-World Validation Report",
        "",
        "## Overview",
        "",
        f"- fixtures_run: {len(pack['fixtures'])}",
        f"- false_positives: {fp}",
        f"- false_negatives: {fn}",
        f"- true_positives: {tp}",
        f"- true_negatives: {tn}",
        "",
        "## High-Integrity Versus Shallow Viral Content",
        "",
        f"- high_integrity_viral favored: {favored_high_integrity}",
        f"- shallow viral-looking favored: {favored_shallow}",
        f"- high-integrity favored over shallow: {favored_high_integrity > favored_shallow}",
        "",
        "## Where InsightDensityValidator Changed Final Outcomes",
        "",
    ]
    if insight_changed_cases:
        for case in insight_changed_cases:
            report_lines.extend(
                [
                    f"- `{case['fixture_id']}` `{case['category']}` final `{case['final_status']}` insight_density_score `{case['insight_density_score']}`.",
                ]
            )
    else:
        report_lines.append("- No cases where InsightDensityValidator materially changed the outcome.")

    report_lines.extend(["", "## Category Summary", ""])
    for category, bucket in per_category.items():
        report_lines.extend(
            [
                f"- `{category}` fixtures `{bucket['fixture_count']}`, expected favored `{bucket['expected_favored_count']}`, actual favored `{bucket['actual_favored_count']}`, false positives `{bucket['false_positives']}`, false negatives `{bucket['false_negatives']}`.",
            ]
        )
    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    failure_lines = [
        "# V6 Real-World Failure Modes",
        "",
        "## Frequent Failure Patterns",
        "",
    ]
    generic_like = [item for item in fixture_results if item["signals"]["generic_motivation_detected"]]
    empty_insight = [item for item in fixture_results if item["signals"]["empty_insight_detected"]]
    hook_mismatch = [item for item in fixture_results if item["signals"]["hook_content_mismatch"]]
    emotional_manip = [item for item in fixture_results if item["signals"]["emotional_manipulation_without_payoff"]]
    identity_bait = [item for item in fixture_results if item["signals"]["identity_bait_without_substance"]]
    shallow_virality = [item for item in fixture_results if item["signals"]["shallow_virality"]]

    failure_lines.extend(
        [
            f"- generic_motivation_detected: {len(generic_like)}",
            f"- empty_insight_detected: {len(empty_insight)}",
            f"- hook_content_mismatch: {len(hook_mismatch)}",
            f"- emotional_manipulation_without_payoff: {len(emotional_manip)}",
            f"- identity_bait_without_substance: {len(identity_bait)}",
            f"- shallow_virality: {len(shallow_virality)}",
            "",
            "## False Positives",
            "",
        ]
    )
    fps = [item for item in fixture_results if not item["expected_favored"] and item["actual_favored"]]
    if fps:
        for item in fps:
            failure_lines.append(f"- `{item['fixture_id']}` `{item['category']}` was incorrectly favored.")
    else:
        failure_lines.append("- None.")

    failure_lines.extend(["", "## False Negatives", ""])
    fns = [item for item in fixture_results if item["expected_favored"] and not item["actual_favored"]]
    if fns:
        for item in fns:
            failure_lines.append(
                f"- `{item['fixture_id']}` `{item['category']}` rejected with insight `{item['scores']['insight_density_score']}` and viral integrity `{item['scores']['viral_integrity_score']}`."
            )
    else:
        failure_lines.append("- None.")
    FAILURE_PATH.write_text("\n".join(failure_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
