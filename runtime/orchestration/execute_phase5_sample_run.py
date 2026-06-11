from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.validation.validator_engine import evaluate_text


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def dedupe_validator_specs(validators: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for item in validators:
        key = item["id"]
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def resolve_libraries(input_bundle: dict, ownership_map: dict, validator_registry: dict) -> dict:
    selected_rules = []
    for item in ownership_map["ownership_assignments"]["rules"]:
        if item["primary_library"] in {
            "continuity_state_library",
            "cadence_library",
            "dialogue_behavior_library",
            "abstraction_control_library",
            "voice_library",
            "genre_library",
        }:
            selected_rules.append(item)

    selected_validators = dedupe_validator_specs(
        [
            {
                "id": item["validator_id"],
                "name": item["validator_id"],
                "primary_library": item["primary_library"],
                "secondary_libraries": item["secondary_libraries"],
            }
            for item in validator_registry["validators"]
        ]
    )

    selected_failure_modes = []
    for item in ownership_map["ownership_assignments"]["failure_modes"]:
        if item["name"] in {
            "cadence_flattening_failure",
            "dialogue_realism_collapse",
            "prose_naturalness_collapse",
            "continuity_memory_failure",
            "over_abstraction_failure",
            "semantic_redundancy_failure",
        }:
            selected_failure_modes.append(item)

    return {
        "run_id": input_bundle["run_id"],
        "mode": input_bundle["mode"],
        "genre": input_bundle["genre"],
        "voice": input_bundle["voice"],
        "resolved_primary_libraries": [
            "system_design_library",
            "genre_library",
            "voice_library",
            "continuity_state_library",
            "cadence_library",
            "dialogue_behavior_library",
            "abstraction_control_library",
            "failure_mode_library",
            "evaluation_library",
            "benchmark_fixture_library",
        ],
        "resolved_secondary_libraries": sorted(
            {
                "human_texture_library",
                "sentence_structure_library",
                "narrative_pressure_library",
            }
        ),
        "resolved_rules": [
            {
                "id": item["id"],
                "name": item["name"],
                "primary_library": item["primary_library"],
                "secondary_libraries": item["secondary_libraries"],
            }
            for item in selected_rules[:12]
        ],
        "resolved_validators": selected_validators,
        "resolved_failure_modes": [
            {
                "id": item["id"],
                "name": item["name"],
                "primary_library": item["primary_library"],
                "secondary_libraries": item["secondary_libraries"],
            }
            for item in selected_failure_modes
        ],
        "validator_pass_registry": validator_registry["validators"],
    }


def generate_draft(_: dict) -> str:
    return (
        "Mara stood on the winter platform with the ticket folded flat inside her glove. "
        "The rail hummed once, then stopped, and the porter looked up as if he had heard her lie before she spoke it. "
        "Cold moved under the roof in brief, needling drafts.\n\n"
        "\"Last boarding,\" the porter said.\n"
        "\"I know,\" Mara said, too quickly.\n\n"
        "She watched the lamps tremble along the train windows and counted the doors instead of the seconds. "
        "If he asked to see the ticket now, the whole decision would harden into something public. "
        "So she stepped closer, calm on the surface, careful in the voice, and let the pause do more work than the sentence."
    )


def run_passes(draft_text: str, input_bundle: dict, thresholds: dict, validator_registry: dict) -> tuple[dict, dict, dict]:
    evaluation_core = evaluate_text(draft_text, input_bundle, thresholds, validator_registry)
    metrics = evaluation_core["metrics"]
    validator_results = evaluation_core["validator_results"]
    threshold_results = evaluation_core["threshold_results"]
    final_status = evaluation_core["final_status"]

    violation_span_lookup = {
        "RULE_DIALOGUE_ACT_DIVERSITY_MIN": "\"Last boarding,\" the porter said.",
        "RULE_SPEAKER_STYLE_DISTANCE_MIN": "\"I know,\" Mara said, too quickly.",
        "RULE_SENTENCE_LENGTH_VAR_MIN": "The rail hummed once, then stopped, and the porter looked up as if he had heard her lie before she spoke it.",
        "RULE_ABSTRACTION_RATIO_MAX": "If he asked to see the ticket now, the whole decision would harden into something public.",
        "RULE_SEMANTIC_REDUNDANCY_CAP": "So she stepped closer, calm on the surface, careful in the voice, and let the pause do more work than the sentence.",
        "RULE_CONTINUITY_CONTRADICTION_CAP": "Mara stood on the winter platform with the ticket folded flat inside her glove.",
    }

    violations = []
    critical_violations = []
    failure_modes = []
    for item in validator_results:
        if item["status"] == "pass":
            continue
        if item["validator_id"] == "cadence_variance_checker":
            payload = {
                "rule_id": "RULE_SENTENCE_LENGTH_VAR_MIN",
                "message": "Cadence variance fell below target minimum.",
                "severity": "warning" if item["status"] == "warn" else "critical",
                "primary_library": "cadence_library",
                "secondary_libraries": ["evaluation_library", "failure_mode_library", "sentence_structure_library"],
                "affected_dimensions": ["cadence"],
                "recommended_action": "Regenerate with stronger sentence-length variance and more structural contrast.",
            }
            failure_modes.append("cadence_flattening_failure")
        elif item["validator_id"] == "abstraction_ratio_checker":
            payload = {
                "rule_id": "RULE_ABSTRACTION_RATIO_MAX",
                "message": "Abstraction ratio exceeded preferred grounded-detail range.",
                "severity": "warning" if item["status"] == "warn" else "critical",
                "primary_library": "abstraction_control_library",
                "secondary_libraries": ["evaluation_library", "failure_mode_library"],
                "affected_dimensions": ["human_texture"],
                "recommended_action": "Regenerate with more concrete scene detail and fewer abstract summaries.",
            }
            failure_modes.extend(["over_abstraction_failure", "prose_naturalness_collapse"])
        elif item["validator_id"] == "semantic_redundancy_detector":
            payload = {
                "rule_id": "RULE_SEMANTIC_REDUNDANCY_CAP",
                "message": "Semantic redundancy exceeded novelty targets.",
                "severity": "warning" if item["status"] == "warn" else "critical",
                "primary_library": "abstraction_control_library",
                "secondary_libraries": ["evaluation_library", "failure_mode_library"],
                "affected_dimensions": ["human_texture"],
                "recommended_action": "Regenerate with higher local novelty and lower phrase repetition.",
            }
            failure_modes.append("semantic_redundancy_failure")
        elif item["validator_id"] == "dialogue_realism_checker":
            payload = {
                "rule_id": "RULE_DIALOGUE_ACT_DIVERSITY_MIN",
                "message": "Dialogue realism and variation remained below target band.",
                "severity": "warning" if item["status"] == "warn" else "critical",
                "primary_library": "dialogue_behavior_library",
                "secondary_libraries": ["evaluation_library", "voice_library"],
                "affected_dimensions": ["dialogue_integrity"],
                "recommended_action": "Regenerate with stronger speaker variation, interruption, or pragmatic texture.",
            }
            failure_modes.append("dialogue_realism_collapse")
        elif item["validator_id"] == "continuity_consistency_checker":
            payload = {
                "rule_id": "RULE_CONTINUITY_CONTRADICTION_CAP",
                "message": "Continuity state check failed.",
                "severity": "critical",
                "primary_library": "continuity_state_library",
                "secondary_libraries": ["evaluation_library", "failure_mode_library"],
                "affected_dimensions": ["continuity"],
                "recommended_action": "Reject and regenerate with corrected state alignment.",
            }
            failure_modes.append("continuity_memory_failure")
        elif item["validator_id"] == "human_style_preference_validator":
            payload = {
                "rule_id": "RULE_STYLE_DISTANCE_MAX",
                "message": "Human style preference target was not met.",
                "severity": "warning" if item["status"] == "warn" else "critical",
                "primary_library": "voice_library",
                "secondary_libraries": ["evaluation_library", "abstraction_control_library"],
                "affected_dimensions": ["human_likeness"],
                "recommended_action": "Regenerate in paragraph-first prose with stronger context depth and lower bullet dependence.",
            }
            failure_modes.append("prose_naturalness_collapse")
        else:
            continue

        if payload["severity"] == "critical":
            critical_violations.append(payload)
        else:
            violations.append(payload)

    warnings = [f"{item['dimension']} is below target minimum but above rejection floor." for item in threshold_results if item["status"] == "warn"]
    blocking_failures = [item["message"] for item in critical_violations]

    evaluation_data = {
        "final_status": final_status,
        "dimension_scores": evaluation_core["dimension_scores"],
        "emotional_energy_score": round(metrics["emotional_energy_score"], 2),
        "paragraph_flow_score": round(metrics["paragraph_flow_score"], 2),
        "context_sufficiency_score": round(metrics["context_sufficiency_score"], 2),
        "validator_results": validator_results,
        "threshold_results": threshold_results,
        "warnings": warnings,
        "blocking_failures": blocking_failures,
        "detected_failure_modes": sorted(set(failure_modes)),
    }

    enforcement_data = {
        "status": "failed" if critical_violations else "warning" if violations else "passed",
        "violations": violations,
        "critical_violations": critical_violations,
        "violation_spans": [
            {
                "rule_id": item["rule_id"],
                "span_text": violation_span_lookup.get(item["rule_id"], ""),
            }
            for item in (critical_violations + violations)
        ],
    }

    failure_map_data = {
        "detected_failure_modes": sorted(set(failure_modes)),
        "severity_bands": {
            "critical": [item["rule_id"] for item in critical_violations],
            "warning": [item["rule_id"] for item in violations],
            "informational": [],
        },
    }
    return evaluation_data, enforcement_data, failure_map_data


def main() -> None:
    run_dir = ROOT / "runs" / "sample_run_001"
    input_bundle = load_json(run_dir / "input_bundle.json")
    ownership_map = load_json(ROOT / "libraries" / "updated_library_crosswalk.json")
    pass_manifest = load_json(ROOT / "runtime" / "orchestration" / "pass_order_manifest.json")
    validator_registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    evaluation_thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")
    eval_template = load_json(ROOT / "evaluation" / "reports" / "evaluation_report.template.json")
    enforcement_template = load_json(ROOT / "evaluation" / "reports" / "enforcement_report.template.json")
    failure_map_template = load_json(ROOT / "evaluation" / "reports" / "failure_map.template.json")
    summary_template = load_json(ROOT / "evaluation" / "reports" / "run_summary.template.json")

    resolved = resolve_libraries(input_bundle, ownership_map, validator_registry)
    draft_text = generate_draft(input_bundle)
    evaluation_data, enforcement_data, failure_map_data = run_passes(draft_text, input_bundle, evaluation_thresholds, validator_registry)

    evaluation_report = deepcopy(eval_template)
    evaluation_report.update(
        {
            "run_id": input_bundle["run_id"],
            "status": evaluation_data["final_status"],
            "mode": input_bundle["mode"],
            "genre": input_bundle["genre"],
            "voice": input_bundle["voice"],
            "dimension_scores": evaluation_data["dimension_scores"],
            "emotional_energy_score": evaluation_data["emotional_energy_score"],
            "paragraph_flow_score": evaluation_data["paragraph_flow_score"],
            "context_sufficiency_score": evaluation_data["context_sufficiency_score"],
            "validator_results": evaluation_data["validator_results"],
            "threshold_results": evaluation_data["threshold_results"],
            "validators_run": [item["validator_id"] for item in validator_registry["validators"]],
            "primary_library_trace": resolved["resolved_primary_libraries"],
            "secondary_library_trace": resolved["resolved_secondary_libraries"],
            "warnings": evaluation_data["warnings"],
            "blocking_failures": evaluation_data["blocking_failures"],
            "evidence_spans": [
                {
                    "pass_id": "cadence_pass",
                    "excerpt": "The rail hummed once, then stopped, and the porter looked up as if he had heard her lie before she spoke it."
                },
                {
                    "pass_id": "dialogue_integrity_pass",
                    "excerpt": "\"Last boarding,\" the porter said. \"I know,\" Mara said, too quickly."
                }
            ],
        }
    )

    all_violations = enforcement_data["critical_violations"] + enforcement_data["violations"]
    enforcement_report = deepcopy(enforcement_template)
    enforcement_report.update(
        {
            "run_id": input_bundle["run_id"],
            "status": enforcement_data["status"],
            "authoritative_rule_set": [item["name"] for item in resolved["resolved_rules"]],
            "violations": enforcement_data["violations"],
            "critical_violations": enforcement_data["critical_violations"],
            "violation_spans": enforcement_data["violation_spans"],
            "affected_dimensions": sorted({dim for item in all_violations for dim in item["affected_dimensions"]}),
            "recommended_action": "deliver_with_warnings" if evaluation_data["final_status"] == "accepted_with_warnings" else "deliver" if evaluation_data["final_status"] == "accepted" else "reject_and_regenerate",
            "severity": "critical" if enforcement_data["critical_violations"] else "warning" if enforcement_data["violations"] else "informational",
            "primary_library": all_violations[0]["primary_library"] if all_violations else "system_design_library",
            "secondary_libraries": all_violations[0]["secondary_libraries"] if all_violations else [],
            "rule_ownership_trace": resolved["resolved_rules"],
            "linked_validators": resolved["resolved_validators"],
            "notes": [
                "Enforcement remains authoritative.",
                "No runtime rules were mutated during execution."
            ],
        }
    )

    failure_map = deepcopy(failure_map_template)
    failure_map.update(
        {
            "run_id": input_bundle["run_id"],
            "detected_failure_modes": failure_map_data["detected_failure_modes"],
            "failure_to_rule_links": [
                {
                    "failure_mode": "dialogue_realism_collapse",
                    "rule_id": "RULE_DIALOGUE_ACT_DIVERSITY_MIN"
                },
                {
                    "failure_mode": "cadence_flattening_failure",
                    "rule_id": "RULE_SENTENCE_LENGTH_VAR_MIN"
                },
                {
                    "failure_mode": "semantic_redundancy_failure",
                    "rule_id": "RULE_SEMANTIC_REDUNDANCY_CAP"
                }
            ],
            "failure_to_validator_links": [
                {
                    "failure_mode": "dialogue_realism_collapse",
                    "validator_id": "dialogue_realism_checker"
                },
                {
                    "failure_mode": "cadence_flattening_failure",
                    "validator_id": "cadence_variance_checker"
                },
                {
                    "failure_mode": "semantic_redundancy_failure",
                    "validator_id": "semantic_redundancy_detector"
                }
            ],
            "severity_bands": failure_map_data["severity_bands"],
            "library_trace": {
                "primary": resolved["resolved_primary_libraries"],
                "secondary": resolved["resolved_secondary_libraries"],
            },
        }
    )

    run_summary = deepcopy(summary_template)
    run_summary.update(
        {
            "run_id": input_bundle["run_id"],
            "final_status": evaluation_data["final_status"],
            "primary_library_trace": resolved["resolved_primary_libraries"],
            "secondary_library_trace": resolved["resolved_secondary_libraries"],
            "blocking_reasons": evaluation_data["blocking_failures"],
            "warning_reasons": evaluation_data["warnings"],
            "next_action": "deliver_with_warnings" if evaluation_data["final_status"] == "accepted_with_warnings" else "deliver" if evaluation_data["final_status"] == "accepted" else "reject_and_regenerate",
            "executed_passes": [item["pass_id"] for item in pass_manifest["execution_order"]],
        }
    )

    write_json(run_dir / "resolved_libraries.json", resolved)
    (run_dir / "draft_output.txt").write_text(draft_text, encoding="utf-8")
    write_json(run_dir / "evaluation_report.json", evaluation_report)
    write_json(run_dir / "enforcement_report.json", enforcement_report)
    write_json(run_dir / "failure_map.json", failure_map)
    write_json(run_dir / "run_summary.json", run_summary)


if __name__ == "__main__":
    main()
