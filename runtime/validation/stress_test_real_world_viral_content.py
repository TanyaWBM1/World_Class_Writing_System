from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.validation.validator_engine import evaluate_text


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")
    suite = load_json(ROOT / "runtime" / "validation" / "real_world_viral_cases.json")

    case_results = []
    for case in suite["cases"]:
        result = evaluate_text(case["proxy_text"], {}, thresholds, registry)
        validators = {item["validator_id"]: item for item in result["validator_results"]}
        viral = result["reader_metrics"]["viral_metrics"]
        case_results.append(
            {
                "case_id": case["case_id"],
                "label": case["label"],
                "source_title": case["source_title"],
                "source_url": case["source_url"],
                "source_date": case["source_date"],
                "expected_profile": case["expected_profile"],
                "final_status": result["final_status"],
                "viral_score": viral["viral_score"],
                "viral_integrity_score": viral["viral_integrity_score"],
                "insight_density_score": viral["insight_density_score"],
                "abstraction_ratio": viral["abstraction_ratio"],
                "concrete_example_count": viral["concrete_example_count"],
                "high_integrity_viral_cases": viral["high_integrity_viral_cases"],
                "generic_motivation_detected": viral["generic_motivation_detected"],
                "empty_insight_detected": viral["empty_insight_detected"],
                "shallow_philosophy_detected": viral["shallow_philosophy_detected"],
                "validator_statuses": {
                    "semantic_redundancy_detector": validators["semantic_redundancy_detector"]["status"],
                    "high_arousal_emotion_validator": validators["high_arousal_emotion_validator"]["status"],
                    "hook_strength_validator": validators["hook_strength_validator"]["status"],
                    "novelty_validator": validators["novelty_validator"]["status"],
                    "insight_density_validator": validators["insight_density_validator"]["status"],
                    "viral_integrity_validator": validators["viral_integrity_validator"]["status"],
                },
            }
        )

    case_results.sort(key=lambda item: (item["viral_score"], item["insight_density_score"]), reverse=True)
    write_json(ROOT / "runtime" / "validation" / "real_world_viral_stress_results.json", {"suite_id": suite["suite_id"], "cases": case_results})

    lines = [
        "# Real-World Viral Content Stress Test",
        "",
        "These are sourced paraphrase proxies of real published pieces or viral framings, not copied article bodies.",
        "",
        "## Results",
        "",
    ]
    for case in case_results:
        lines.extend(
            [
                f"## {case['label']}",
                "",
                f"- source_title: {case['source_title']}",
                f"- source_date: {case['source_date']}",
                f"- final_status: {case['final_status']}",
                f"- viral_score: {case['viral_score']}",
                f"- viral_integrity_score: {case['viral_integrity_score']}",
                f"- insight_density_score: {case['insight_density_score']}",
                f"- abstraction_ratio: {case['abstraction_ratio']}",
                f"- concrete_example_count: {case['concrete_example_count']}",
                f"- high_integrity_viral_cases: {case['high_integrity_viral_cases']}",
                f"- generic_motivation_detected: {case['generic_motivation_detected']}",
                f"- empty_insight_detected: {case['empty_insight_detected']}",
                f"- shallow_philosophy_detected: {case['shallow_philosophy_detected']}",
                "",
            ]
        )
    (ROOT / "runtime" / "validation" / "real_world_viral_stress_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
