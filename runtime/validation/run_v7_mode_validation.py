from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.generation.v7_generator import run_generation


OUTPUT_JSON = ROOT / "runtime" / "validation" / "v7_mode_comparison.json"
OUTPUT_MD = ROOT / "runtime" / "validation" / "v7_mode_validation_report.md"


TEST_CASES = [
    {
        "case_id": "utility_mode_case",
        "expected_mode": "utility",
        "profile": {
            "mode": "utility",
            "genre": "answer_first_guide",
            "audience": "time-constrained operators",
            "target_platform": "reddit",
            "topic": "how to verify whether a leaked screenshot is real",
            "desired_reader_impact": "clarity and confidence",
            "desired_viral_profile": "useful and trustworthy",
            "prompt_brief": "guide, definition, steps, evidence",
        },
    },
    {
        "case_id": "narrative_mode_case",
        "expected_mode": "narrative",
        "profile": {
            "mode": "narrative",
            "genre": "essayistic_story_post",
            "audience": "reflective readers",
            "target_platform": "facebook",
            "topic": "how a single hospital hallway conversation changed what a family could admit out loud",
            "desired_reader_impact": "resonance and memory",
            "desired_viral_profile": "high-integrity emotional spread",
            "prompt_brief": "story, memory, resonance, emotion",
        },
    },
    {
        "case_id": "authority_mode_case",
        "expected_mode": "authority",
        "profile": {
            "mode": "authority",
            "genre": "evidence_backed_explainer",
            "audience": "decision-makers",
            "target_platform": "linkedin",
            "topic": "why one audit trail can collapse a polished institutional falsehood",
            "desired_reader_impact": "trust and comprehension",
            "desired_viral_profile": "credible, discussable, high-integrity",
            "prompt_brief": "prove, explain reality, evidence, authority",
        },
    },
]


def validator_map(results: list[dict]) -> dict[str, dict]:
    return {item["validator_id"]: item for item in results}


def compact_weights(weights: dict[str, float]) -> list[dict]:
    return [
        {"pillar": pillar, "weight": weight}
        for pillar, weight in sorted(weights.items(), key=lambda item: item[1], reverse=True)
    ]


def derive_strengths(vmap: dict[str, dict]) -> list[str]:
    strengths = []
    if vmap["heo_override_validator"]["status"] == "pass":
        strengths.append("HEO override remained inactive")
    if vmap["pillar_coverage_validator"]["score"] >= 0.55:
        strengths.append("pillar coverage stayed materially aligned with the selected mode")
    if vmap["dual_lane_validator"]["score"] >= 0.58:
        strengths.append("dual-lane balance remained stable")
    if vmap["human_likeness_discriminator"]["status"] == "pass":
        strengths.append("core v3-v6 stack still produced a passing human-likeness signal")
    return strengths


def derive_misalignments(vmap: dict[str, dict]) -> list[str]:
    misalignments = []
    if vmap["mode_alignment_validator"]["status"] != "pass":
        misalignments.append("mode-alignment score did not fully clear the preferred band")
    if vmap["pillar_coverage_validator"]["evidence"].get("uncovered_pillars"):
        misalignments.append(
            "uncovered pillars: " + ", ".join(vmap["pillar_coverage_validator"]["evidence"]["uncovered_pillars"])
        )
    if vmap["dialogue_realism_checker"]["status"] == "fail":
        misalignments.append("dialogue realism failed because the generator produced prose-only output")
    if vmap["surprise_calibration_validator"]["status"] == "fail":
        misalignments.append("surprise remained low, which limits viral lift")
    return misalignments


def summarize_failures(vmap: dict[str, dict]) -> list[dict]:
    items = []
    for validator_id, result in vmap.items():
        if result["status"] in {"warn", "fail"}:
            items.append(
                {
                    "validator_id": validator_id,
                    "status": result["status"],
                    "score": result.get("score"),
                }
            )
    return items


def mode_behavior_matched(case: dict, mode_selection: dict, vmap: dict[str, dict]) -> bool:
    return (
        mode_selection["mode_id"] == case["expected_mode"]
        and vmap["heo_override_validator"]["status"] == "pass"
        and vmap["dual_lane_validator"]["score"] >= 0.55
    )


def build_case_result(case: dict) -> dict:
    run = run_generation(case["profile"])
    selected = run["evaluation_report_compatible"]
    vmap = validator_map(selected["validator_results"])
    mode_selection = run["mode_selection"]
    weights = mode_selection["weighting_profile"]["weights"]
    return {
        "case_id": case["case_id"],
        "expected_mode": case["expected_mode"],
        "selected_mode": mode_selection["mode_id"],
        "mode_selection_valid": mode_selection["mode_id"] == case["expected_mode"],
        "weighting_profile": {
            "rationale": mode_selection["weighting_profile"]["rationale"],
            "weights_ranked": compact_weights(weights),
        },
        "selected_candidate_id": run["selected_candidate_id"],
        "selected_output": run["selected_output"],
        "heo_override_active": vmap["heo_override_validator"]["evidence"]["override_triggered"],
        "v3_v6_core_health": {
            "human_likeness_status": vmap["human_likeness_discriminator"]["status"],
            "reader_impact_score": next(
                (
                    item["score"]
                    for item in selected["validator_results"]
                    if item.get("dimension") == "reader_impact"
                ),
                None,
            ),
            "viral_integrity_status": vmap["viral_integrity_validator"]["status"],
            "insight_density_status": vmap["insight_density_validator"]["status"],
        },
        "strengths": derive_strengths(vmap),
        "misalignments": derive_misalignments(vmap),
        "validator_failures_or_warnings": summarize_failures(vmap),
        "mode_behavior_matched_expectation": mode_behavior_matched(case, mode_selection, vmap),
        "v7_scores": {
            "mode_alignment_score": vmap["mode_alignment_validator"]["score"],
            "dual_lane_score": vmap["dual_lane_validator"]["score"],
            "pillar_coverage_score": vmap["pillar_coverage_validator"]["score"],
        },
    }


def write_markdown(results: list[dict]) -> None:
    lines = ["# V7 Mode Validation Report", ""]
    for item in results:
        lines.extend(
            [
                f"## {item['case_id']}",
                "",
                f"- selected_mode: `{item['selected_mode']}`",
                f"- expected_mode: `{item['expected_mode']}`",
                f"- mode_selection_valid: `{str(item['mode_selection_valid']).lower()}`",
                f"- heo_override_active: `{str(item['heo_override_active']).lower()}`",
                f"- selected_candidate_id: `{item['selected_candidate_id']}`",
                f"- mode_alignment_score: `{item['v7_scores']['mode_alignment_score']}`",
                f"- dual_lane_score: `{item['v7_scores']['dual_lane_score']}`",
                f"- pillar_coverage_score: `{item['v7_scores']['pillar_coverage_score']}`",
                "",
                "### Weighting Profile",
                "",
            ]
        )
        for entry in item["weighting_profile"]["weights_ranked"]:
            lines.append(f"- {entry['pillar']}: `{entry['weight']}`")
        lines.extend(
            [
                "",
                "### Output",
                "",
                item["selected_output"],
                "",
                "### Strengths",
                "",
            ]
        )
        for strength in item["strengths"]:
            lines.append(f"- {strength}")
        lines.extend(["", "### Misalignments", ""])
        for misalignment in item["misalignments"]:
            lines.append(f"- {misalignment}")
        lines.extend(["", "### Validator Failures Or Warnings", ""])
        for issue in item["validator_failures_or_warnings"]:
            lines.append(
                f"- {issue['validator_id']}: `{issue['status']}` ({issue['score']})"
            )
        lines.extend(
            [
                "",
                "### Expectation Match",
                "",
                f"- mode_behavior_matched_expectation: `{str(item['mode_behavior_matched_expectation']).lower()}`",
                "",
            ]
        )

    OUTPUT_MD.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    results = [build_case_result(case) for case in TEST_CASES]
    summary = {
        "run_id": "v7_mode_validation_001",
        "cases": results,
        "all_mode_selection_valid": all(item["mode_selection_valid"] for item in results),
        "all_weighting_profiles_present": all(item["weighting_profile"]["weights_ranked"] for item in results),
        "generator_behavior_valid": all(item["mode_behavior_matched_expectation"] for item in results),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(results)


if __name__ == "__main__":
    main()
