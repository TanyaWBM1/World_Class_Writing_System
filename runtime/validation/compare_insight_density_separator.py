from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.validation.validator_engine import evaluate_text


OUTPUT_JSON = ROOT / "runtime" / "validation" / "insight_density_separator_comparison.json"
OUTPUT_MD = ROOT / "runtime" / "validation" / "insight_density_separator_comparison.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def summarize_case(case_id: str, text: str, thresholds: dict, registry: dict) -> dict:
    result = evaluate_text(text, {}, thresholds, registry)
    validators = {item["validator_id"]: item for item in result["validator_results"]}
    viral = result["reader_metrics"]["viral_metrics"]
    return {
        "case_id": case_id,
        "final_status": result["final_status"],
        "viral_score": viral["viral_score"],
        "viral_integrity_score": viral["viral_integrity_score"],
        "insight_density_score": viral["insight_density_score"],
        "abstraction_ratio": viral["abstraction_ratio"],
        "concrete_example_count": viral["concrete_example_count"],
        "generic_motivation_detected": viral["generic_motivation_detected"],
        "empty_insight_detected": viral["empty_insight_detected"],
        "shallow_philosophy_detected": viral["shallow_philosophy_detected"],
        "high_integrity_viral_cases": viral["high_integrity_viral_cases"],
        "validator_statuses": {
            "insight_density_validator": validators["insight_density_validator"]["status"],
            "viral_integrity_validator": validators["viral_integrity_validator"]["status"],
            "hook_strength_validator": validators["hook_strength_validator"]["status"],
            "shareability_validator": validators["shareability_validator"]["status"],
            "novelty_validator": validators["novelty_validator"]["status"],
        },
    }


def main() -> None:
    registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")
    adversarial_suite = load_json(ROOT / "libraries" / "benchmark_fixture_library" / "entries" / "v6_adversarial_viral_suite.json")
    viral_suite = load_json(ROOT / "libraries" / "benchmark_fixture_library" / "entries" / "v6_viral_suite.json")

    high_integrity_text = next(
        fixture["text_under_test"]
        for fixture in adversarial_suite["fixtures"]
        if fixture["fixture_id"] == "v6_viral_integrity_pass_001"
    )
    generic_text = next(
        fixture["text_under_test"]
        for fixture in viral_suite["fixtures"]
        if fixture["fixture_id"] == "v6_generic_viral_looking_fail_001"
    )

    high_case = summarize_case("high_integrity_viral_piece", high_integrity_text, thresholds, registry)
    generic_case = summarize_case("generic_viral_looking_piece", generic_text, thresholds, registry)

    separator = {
        "separator_validator": "insight_density_validator",
        "high_integrity_case": high_case,
        "generic_case": generic_case,
        "delta": {
            "insight_density_score": round(high_case["insight_density_score"] - generic_case["insight_density_score"], 3),
            "abstraction_ratio": round(high_case["abstraction_ratio"] - generic_case["abstraction_ratio"], 3),
            "concrete_example_count": high_case["concrete_example_count"] - generic_case["concrete_example_count"],
            "viral_score": round(high_case["viral_score"] - generic_case["viral_score"], 3),
        },
        "verdict": {
            "insight_density_is_primary_separator": (
                high_case["validator_statuses"]["insight_density_validator"] != generic_case["validator_statuses"]["insight_density_validator"]
                and high_case["insight_density_score"] > generic_case["insight_density_score"]
                and high_case["concrete_example_count"] > generic_case["concrete_example_count"]
                and high_case["generic_motivation_detected"] is False
                and generic_case["generic_motivation_detected"] is True
            ),
            "notes": [
                "Both pieces are evaluated by the same v6 stack.",
                "The high-integrity piece remains admissible because concrete support and idea density offset lower viral-growth subdimensions.",
                "The generic piece collapses on insight density despite portable phrasing."
            ],
        },
    }
    write_json(OUTPUT_JSON, separator)

    lines = [
        "# Insight Density Separator Comparison",
        "",
        "## Cases",
        "",
        f"- High-integrity viral piece: `{high_case['final_status']}`",
        f"- Generic viral-looking piece: `{generic_case['final_status']}`",
        "",
        "## Core Separation",
        "",
        f"- insight_density_score: {high_case['insight_density_score']} vs {generic_case['insight_density_score']}",
        f"- abstraction_ratio: {high_case['abstraction_ratio']} vs {generic_case['abstraction_ratio']}",
        f"- concrete_example_count: {high_case['concrete_example_count']} vs {generic_case['concrete_example_count']}",
        f"- generic_motivation_detected: {high_case['generic_motivation_detected']} vs {generic_case['generic_motivation_detected']}",
        f"- empty_insight_detected: {high_case['empty_insight_detected']} vs {generic_case['empty_insight_detected']}",
        f"- shallow_philosophy_detected: {high_case['shallow_philosophy_detected']} vs {generic_case['shallow_philosophy_detected']}",
        "",
        "## Verdict",
        "",
        f"- InsightDensityValidator is the separating validator: {separator['verdict']['insight_density_is_primary_separator']}",
        "- It is not the only differing signal, but it is the clearest value-layer discriminator between the two cases.",
        "- The high-integrity case carries concrete support and avoids generic uplift language.",
        "- The generic case uses portable motivation language without enough idea density to survive v6 gating.",
    ]
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
