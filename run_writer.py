from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.cli.cli_parser import parse_cli_args
from runtime.generation.v7_generator import run_generation
from runtime.mode_system.mode_selection_engine import filter_validator_registry_for_profile, select_mode
from runtime.phrase_system.phrase_runtime import phrase_analysis
from runtime.validation.dual_lane_validator import evaluate_dual_lane
from runtime.validation.grit_appropriateness_validator import evaluate_grit_appropriateness
from runtime.validation.grit_phrase_reuse_validator import evaluate_grit_phrase_reuse
from runtime.validation.heo_override_validator import evaluate_heo_override
from runtime.validation.human_likeness_validator import evaluate_human_likeness
from runtime.validation.lexical_grounding_validator import evaluate_lexical_grounding
from runtime.validation.metaphor_overuse_validator import evaluate_metaphor_overuse
from runtime.validation.mode_alignment_validator import evaluate_mode_alignment
from runtime.validation.phrase_repetition_validator import evaluate_phrase_repetition
from runtime.validation.pillar_coverage_validator import evaluate_pillar_coverage
from runtime.validation.rhetorical_frame_repetition_validator import evaluate_rhetorical_frame_repetition
from runtime.validation.cadence_validator import evaluate_cadence
from runtime.validation.thought_visibility_validator import evaluate_thought_visibility
from runtime.validation.style_drift_detector import evaluate_style_drift
from runtime.validation.validator_engine import evaluate_text
from runtime.validation.mode_enforcement_validator import evaluate_mode_enforcement
from runtime.validation.voice_consistency_validator import evaluate_voice_consistency
from runtime.voice_system.voice_runtime import analyze_lexical_grounding, analyze_voice_text


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def make_run_id() -> str:
    return f"local_cli_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def build_run_config(args) -> dict:
    target_platform = "general distribution" if args.platform == "none" else args.platform
    return {
        "run_id": make_run_id(),
        "topic": args.topic,
        "mode": args.mode,
        "grit": args.grit,
        "platform": args.platform,
        "length": args.length,
        "voice_profile": args.voice_profile,
        "output_dir": str(args.output_dir),
        "dry_run": args.dry_run,
        "generator_profile": {
            "mode": args.mode,
            "genre": f"{args.mode}_{args.length}_form_piece",
            "audience": "general intelligent internet readers",
            "target_platform": target_platform,
            "topic": args.topic,
            "prompt_brief": args.topic,
            "desired_reader_impact": {
                "narrative": "memory, resonance, and human recognition",
                "authority": "trust, clarity, and evidence-backed understanding",
                "utility": "clarity, portability, and immediate usability",
                "hybrid": "high-integrity portable insight",
                "creative_writing": "imagination, resonance, and human memory retention",
                "acf_lite": "clarity, accuracy, and evidence-backed explanation without invention",
            }[args.mode],
            "desired_viral_profile": "high_integrity",
            "requested_grit_level": args.grit,
            "voice_profile": args.voice_profile,
            "length": args.length,
            "creative_writing_mode": args.mode == "creative_writing",
            "acf_lite_mode": args.mode == "acf_lite",
            "claim": getattr(args, "claim", ""),
            "defined_window": getattr(args, "defined_window", ""),
            "external_collider": getattr(args, "external_collider", ""),
            "uncertainty_sentence": getattr(args, "uncertainty_sentence", ""),
            "outcome_window": getattr(args, "outcome_window", ""),
            "allowed_blacklist_terms": [args.topic],
            "recent_grit_phrases": [],
            "recent_grit_phrase_counts": {},
            "current_draft_grit_phrases": [],
        },
    }


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
            "generic_motivation_failure",
            "clickbait_pattern_failure",
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


def build_input_bundle(run_config: dict) -> dict:
    profile = run_config["generator_profile"]
    return {
        "run_id": run_config["run_id"],
        "mode": profile["mode"],
        "genre": profile["genre"],
        "voice": run_config["voice_profile"],
        "platform": run_config["platform"],
        "length": run_config["length"],
        "topic": run_config["topic"],
        "dry_run": run_config["dry_run"],
        "prompt": run_config["topic"],
        "execution_metadata": {
            "entrypoint": "run_writer.py",
            "generated_at": datetime.now().isoformat(),
            "generator_version": "v7",
        },
        "normalized_inputs": run_config,
    }


def build_enforcement_report(
    evaluation_report: dict,
    resolved_libraries: dict,
    enforcement_template: dict,
) -> dict:
    violations = []
    critical_violations = []
    for item in evaluation_report["validator_results"]:
        if item["status"] not in {"warn", "fail"}:
            continue
        payload = {
            "rule_id": item["linked_rules"][0] if item["linked_rules"] else item["validator_id"],
            "message": f"{item['dimension']} fell below target on {item['validator_id']}.",
            "severity": "critical" if item["status"] == "fail" else "warning",
            "primary_library": item["primary_library"],
            "secondary_libraries": item["secondary_libraries"],
            "affected_dimensions": [item["dimension"]],
            "recommended_action": "reject_and_regenerate" if item["status"] == "fail" else "deliver_with_warnings",
        }
        if item["status"] == "fail":
            critical_violations.append(payload)
        else:
            violations.append(payload)

    all_violations = critical_violations + violations
    status = "failed" if critical_violations else "warning" if violations else "passed"
    severity = "critical" if critical_violations else "warning" if violations else "informational"
    recommended_action = (
        "reject_and_regenerate"
        if evaluation_report["status"] == "rejected"
        else "deliver_with_warnings"
        if evaluation_report["status"] == "accepted_with_warnings"
        else "deliver"
    )

    report = deepcopy(enforcement_template)
    report.update(
        {
            "run_id": evaluation_report["run_id"],
            "status": status,
            "authoritative_rule_set": [item["name"] for item in resolved_libraries["resolved_rules"]],
            "violations": violations,
            "critical_violations": critical_violations,
            "violation_spans": [
                {
                    "rule_id": item["rule_id"],
                    "span_text": "",
                }
                for item in all_violations
            ],
            "affected_dimensions": sorted({dim for item in all_violations for dim in item["affected_dimensions"]}),
            "recommended_action": recommended_action,
            "severity": severity,
            "primary_library": all_violations[0]["primary_library"] if all_violations else "system_design_library",
            "secondary_libraries": all_violations[0]["secondary_libraries"] if all_violations else [],
            "rule_ownership_trace": resolved_libraries["resolved_rules"],
            "linked_validators": resolved_libraries["resolved_validators"],
            "notes": [
                "Enforcement remains authoritative.",
                "No runtime rules were mutated during execution.",
            ],
        }
    )
    return report


def build_reports(run_config: dict, generation_result: dict, resolved_libraries: dict) -> tuple[dict, dict, dict]:
    thresholds = load_json(ROOT / "runtime" / "validation" / "evaluation_thresholds.json")
    validator_registry = filter_validator_registry_for_profile(
        run_config["generator_profile"],
        load_json(ROOT / "runtime" / "validation" / "validator_registry.json"),
    )
    eval_template = load_json(ROOT / "evaluation" / "reports" / "evaluation_report.template.json")
    enforcement_template = load_json(ROOT / "evaluation" / "reports" / "enforcement_report.template.json")
    summary_template = load_json(ROOT / "evaluation" / "reports" / "run_summary.template.json")

    profile = run_config["generator_profile"]
    text = generation_result["selected_output"]
    mode_selection = select_mode(profile)
    base_report = evaluate_text(text, {}, thresholds, validator_registry)
    mode_id = mode_selection["mode_id"]
    grit_level = generation_result["evaluation_report_compatible"]["v7_2_grit_context"]["grit_level"]

    mode_result = evaluate_mode_alignment(mode_selection, base_report)
    dual_lane_result = evaluate_dual_lane(
        load_json(ROOT / "runtime" / "pillar_weighting" / "weighting_profiles.json"),
        base_report,
    )
    pillar_result = evaluate_pillar_coverage(mode_selection, base_report)
    heo_result = evaluate_heo_override(base_report)
    voice_result = evaluate_voice_consistency(text, mode_id)
    drift_result = evaluate_style_drift(text, mode_id)
    human_voice_result = evaluate_human_likeness(text, mode_id)
    grit_result = evaluate_grit_appropriateness(
        generation_result["evaluation_report_compatible"]["v7_2_grit_context"],
        profile,
    )
    phrase_result = evaluate_phrase_repetition(text, grit_level)
    rhetorical_result = evaluate_rhetorical_frame_repetition(text, grit_level)
    metaphor_result = evaluate_metaphor_overuse(text, grit_level)
    grit_phrase_result = evaluate_grit_phrase_reuse(text, grit_level)
    lexical_result = evaluate_lexical_grounding(text, mode_id, profile)
    mode_enforcement_result = evaluate_mode_enforcement(text, profile)
    cadence_result = evaluate_cadence(text)
    thought_visibility_result = evaluate_thought_visibility(text)
    v7_validator_results = {
        "mode_alignment_validator": mode_result,
        "dual_lane_validator": dual_lane_result,
        "pillar_coverage_validator": pillar_result,
        "heo_override_validator": heo_result,
        "voice_consistency_validator": voice_result,
        "style_drift_detector": drift_result,
        "human_likeness_validator": human_voice_result,
        "grit_appropriateness_validator": grit_result,
        "phrase_repetition_validator": phrase_result,
        "rhetorical_frame_repetition_validator": rhetorical_result,
        "metaphor_overuse_validator": metaphor_result,
        "grit_phrase_reuse_validator": grit_phrase_result,
        "lexical_grounding_validator": lexical_result,
        "mode_enforcement_validator": mode_enforcement_result,
        "cadence_validator": cadence_result,
        "thought_visibility_validator": thought_visibility_result,
    }
    voice_analysis = analyze_voice_text(text, mode_id)
    lexical_analysis = analyze_lexical_grounding(text, context=profile)
    phrase_context = {
        "controls_applied": generation_result["evaluation_report_compatible"]["v7_3_phrase_context"].get("controls_applied", []),
        "post_control_analysis": phrase_analysis(text, grit_level),
    }
    evaluation_report = deepcopy(eval_template)
    evaluation_report.update(
        {
            "template_id": "evaluation_report_template_v1",
            "run_id": run_config["run_id"],
            "status": base_report["final_status"],
            "mode": run_config["mode"],
            "genre": profile["genre"],
            "voice": run_config["voice_profile"],
            "dimension_scores": base_report["dimension_scores"],
            "validator_results": base_report["validator_results"],
            "threshold_results": base_report["threshold_results"],
            "validators_run": [item["validator_id"] for item in validator_registry["validators"]],
            "primary_library_trace": resolved_libraries["resolved_primary_libraries"],
            "secondary_library_trace": resolved_libraries["resolved_secondary_libraries"],
            "warnings": [
                f"{item['dimension']} is below target minimum but above rejection floor."
                for item in base_report["threshold_results"]
                if item["status"] == "warn"
            ],
            "blocking_failures": [
                f"{item['dimension']} failed its gating threshold."
                for item in base_report["threshold_results"]
                if item["status"] == "fail"
            ],
            "v7_mode_context": {
                "mode_id": mode_selection["mode_id"],
                "dominant_pillars": mode_selection["dominant_pillars"],
                "supporting_pillars": mode_selection["supporting_pillars"],
                "selection_evidence": mode_selection["selection_evidence"],
            },
            "v7_pillar_weighting_context": mode_selection["weighting_profile"],
            "v7_1_voice_context": generation_result["evaluation_report_compatible"]["v7_1_voice_context"],
            "v7_2_grit_context": generation_result["evaluation_report_compatible"]["v7_2_grit_context"],
            "v7_3_phrase_context": phrase_context,
            "v7_validator_results": v7_validator_results,
            "selected_mode": profile.get("selected_mode", profile.get("mode", "")),
            "mode_contract_applied": profile.get("mode_contract_applied", {}),
            "acf_requirements_active": profile.get("acf_requirements_active", False),
            "imagination_allowed": profile.get("imagination_allowed", True),
            "human_texture_allowed": profile.get("human_texture_allowed", True),
            "mode_violation_flags": mode_enforcement_result["evidence"]["mode_violation_flags"],
            "cadence_naturalness_score": cadence_result["evidence"]["cadence_naturalness_score"],
            "compression_flags": cadence_result["evidence"]["compression_flags"],
            "development_depth_score": cadence_result["evidence"]["development_depth_score"],
            "thought_visibility_score": thought_visibility_result["evidence"]["thought_visibility_score"],
            "summarization_flags": thought_visibility_result["evidence"]["summarization_flags"],
            "experience_presence_score": thought_visibility_result["evidence"]["experience_presence_score"],
            "roughness_score": thought_visibility_result["evidence"]["roughness_score"],
            "over_polish_flags": thought_visibility_result["evidence"]["over_polish_flags"],
            "tension_presence_score": thought_visibility_result["evidence"]["tension_presence_score"],
            "emotional_energy_score": round(base_report["metrics"]["emotional_energy_score"], 3),
            "paragraph_flow_score": round(base_report["metrics"]["paragraph_flow_score"], 3),
            "context_sufficiency_score": round(base_report["metrics"]["context_sufficiency_score"], 3),
            "reader_state": base_report["reader_metrics"].get("reader_state", {}),
            "emotional_resonance_score": base_report["reader_metrics"].get("emotional_resonance_score", 0.0),
            "payoff_satisfaction_score": base_report["reader_metrics"].get("payoff_satisfaction_score", 0.0),
            "surprise_score": base_report["reader_metrics"].get("surprise_score", 0.0),
            "tension_absorption_score": base_report["reader_metrics"].get("tension_absorption_score", 0.0),
            "memorability_score": base_report["reader_metrics"].get("memorability_score", 0.0),
            "cognitive_load_score": base_report["reader_metrics"].get("cognitive_load_score", 0.0),
            "high_arousal_score": base_report["reader_metrics"]["viral_metrics"].get("high_arousal_score", 0.0),
            "hook_strength_score": base_report["reader_metrics"]["viral_metrics"].get("hook_strength_score", 0.0),
            "identity_resonance_score": base_report["reader_metrics"]["viral_metrics"].get("identity_resonance_score", 0.0),
            "shareability_score": base_report["reader_metrics"]["viral_metrics"].get("shareability_score", 0.0),
            "novelty_score": base_report["reader_metrics"]["viral_metrics"].get("novelty_score", 0.0),
            "insight_density_score": base_report["reader_metrics"]["viral_metrics"].get("insight_density_score", 0.0),
            "abstraction_ratio": base_report["reader_metrics"]["viral_metrics"].get("abstraction_ratio", 0.0),
            "concrete_example_count": base_report["reader_metrics"]["viral_metrics"].get("concrete_example_count", 0),
            "articulated_takeaway_count": base_report["reader_metrics"]["viral_metrics"].get("articulated_takeaway_count", 0),
            "claim_density": base_report["reader_metrics"]["viral_metrics"].get("claim_density", 0.0),
            "experiential_specificity_score": base_report["reader_metrics"]["viral_metrics"].get("experiential_specificity_score", 0.0),
            "human_stakes_score": base_report["reader_metrics"]["viral_metrics"].get("human_stakes_score", 0.0),
            "interpretive_density_score": base_report["reader_metrics"]["viral_metrics"].get("interpretive_density_score", 0.0),
            "memorable_meaning_score": base_report["reader_metrics"]["viral_metrics"].get("memorable_meaning_score", 0.0),
            "viral_score": base_report["reader_metrics"]["viral_metrics"].get("viral_score", 0.0),
            "viral_integrity_score": base_report["reader_metrics"]["viral_metrics"].get("viral_integrity_score", 0.0),
            "manipulation_risk": base_report["reader_metrics"]["viral_metrics"].get("manipulation_risk", 0.0),
            "clickbait_risk": base_report["reader_metrics"]["viral_metrics"].get("clickbait_risk", 0.0),
            "facebook_score": base_report["platform_metrics"].get("facebook_score", 0.0),
            "youtube_score": base_report["platform_metrics"].get("youtube_score", 0.0),
            "twitter_score": base_report["platform_metrics"].get("twitter_score", 0.0),
            "linkedin_score": base_report["platform_metrics"].get("linkedin_score", 0.0),
            "instagram_score": base_report["platform_metrics"].get("instagram_score", 0.0),
            "reddit_score": base_report["platform_metrics"].get("reddit_score", 0.0),
            "platform_fit_score": base_report["platform_metrics"].get("platform_fit_score", 0.0),
            "platform_fit_analysis": {
                "tone_mismatch": base_report["platform_metrics"].get("tone_mismatch", []),
                "structure_mismatch": base_report["platform_metrics"].get("structure_mismatch", []),
                "audience_mismatch": base_report["platform_metrics"].get("audience_mismatch", []),
                "best_fit_platforms": base_report["platform_metrics"].get("best_fit_platforms", []),
                "weak_fit_platforms": base_report["platform_metrics"].get("weak_fit_platforms", []),
            },
            "voice_alignment_score": voice_result["score"],
            "style_consistency_score": drift_result["score"],
            "human_likeness_score": human_voice_result["score"],
            "marketer_voice_risk": voice_analysis["marketer_voice_risk"],
            "corporate_language_risk": voice_analysis["corporate_language_risk"],
            "generic_motivation_risk": voice_analysis["generic_motivation_risk"],
            "list_overuse_risk": voice_analysis["list_overuse_risk"],
            "lived_grounding_score": voice_analysis["lived_grounding_score"],
            "cultural_spiritual_grounding_score": voice_analysis["cultural_spiritual_grounding_score"],
            "grit_level": grit_level,
            "grit_force_score": grit_result["score"],
            "heo_violation_risk": 0.0 if heo_result["status"] == "pass" else 1.0,
            "phrase_diversity_score": phrase_context["post_control_analysis"]["phrase_diversity_score"],
            "exact_repetition_count": phrase_context["post_control_analysis"]["exact_repetition_count"],
            "near_duplicate_phrase_count": phrase_context["post_control_analysis"]["near_duplicate_phrase_count"],
            "grit_phrase_reuse_risk": phrase_context["post_control_analysis"]["grit_phrase_reuse_risk"],
            "grit_cooldown_applied": generation_result["evaluation_report_compatible"]["v7_2_grit_context"]["grit_cooldown_applied"],
            "cooled_down_phrases": generation_result["evaluation_report_compatible"]["v7_2_grit_context"]["cooled_down_phrases"],
            "metaphor_overuse_risk": phrase_context["post_control_analysis"]["metaphor_overuse_risk"],
            "signature_phrase_overuse_flag": phrase_context["post_control_analysis"]["signature_phrase_overuse_flag"],
            "lexical_alignment_score": lexical_analysis["lexical_alignment_score"],
            "abstract_word_ratio": lexical_analysis["abstract_word_ratio"],
            "flagged_terms": lexical_analysis["flagged_terms"],
            "thread_dropouts": base_report["narrative_metrics"].get("thread_dropouts", []),
            "unpaid_setups": base_report["narrative_metrics"].get("unpaid_setups", []),
            "unsupported_payoffs": base_report["narrative_metrics"].get("unsupported_payoffs", []),
            "arc_jump_candidates": base_report["narrative_metrics"].get("arc_jump_candidates", []),
            "theme_stagnation_points": base_report["narrative_metrics"].get("theme_stagnation_points", []),
            "pressure_flatlines": base_report["narrative_metrics"].get("pressure_flatlines", []),
            "consequence_gaps": base_report["narrative_metrics"].get("consequence_gaps", []),
            "obligation_violations": base_report["narrative_metrics"].get("obligation_violations", []),
            "unmet_setups": base_report["narrative_metrics"].get("unmet_setups", []),
            "unresolved_threads": base_report["narrative_metrics"].get("unresolved_threads", []),
            "arc_stagnation_flags": base_report["narrative_metrics"].get("arc_stagnation_flags", []),
            "motif_failures": base_report["narrative_metrics"].get("motif_failures", []),
            "structural_violation_score": base_report["narrative_metrics"].get("structural_violation_score", 0.0),
            "obligation_failure_count": base_report["narrative_metrics"].get("obligation_failure_count", 0),
        }
    )
    enforcement_report = build_enforcement_report(evaluation_report, resolved_libraries, enforcement_template)
    run_summary = deepcopy(summary_template)
    run_summary.update(
        {
            "run_id": run_config["run_id"],
            "final_status": evaluation_report["status"],
            "artifacts_emitted": [
                "input_bundle.json",
                "resolved_libraries.json",
                "generated_output.txt",
                "evaluation_report.json",
                "enforcement_report.json",
                "run_summary.json",
            ],
            "primary_library_trace": resolved_libraries["resolved_primary_libraries"],
            "secondary_library_trace": resolved_libraries["resolved_secondary_libraries"],
            "blocking_reasons": evaluation_report["blocking_failures"],
            "warning_reasons": evaluation_report["warnings"],
            "next_action": enforcement_report["recommended_action"],
            "executed_passes": [item["pass_id"] for item in load_json(ROOT / "runtime" / "orchestration" / "pass_order_manifest.json")["execution_order"]],
        }
    )
    return evaluation_report, enforcement_report, run_summary


def main() -> int:
    try:
        args = parse_cli_args()
    except SystemExit as exc:
        return int(exc.code)

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"selected mode: {args.mode}")
    print(f"selected grit: {args.grit}")
    print(f"selected voice profile: {args.voice_profile}")
    print(f"output path: {output_dir}")

    run_config = build_run_config(args)
    input_bundle = build_input_bundle(run_config)
    write_json(output_dir / "input_bundle.json", input_bundle)

    if args.dry_run:
        print("final status: dry_run_complete")
        return 0

    generation_result = run_generation(run_config["generator_profile"])
    ownership_map = load_json(ROOT / "libraries" / "updated_library_crosswalk.json")
    validator_registry = load_json(ROOT / "runtime" / "validation" / "validator_registry.json")
    resolved_libraries = resolve_libraries(input_bundle, ownership_map, validator_registry)
    write_json(output_dir / "resolved_libraries.json", resolved_libraries)

    generated_output = generation_result["selected_output"]
    (output_dir / "generated_output.txt").write_text(generated_output, encoding="utf-8")

    evaluation_report, enforcement_report, run_summary = build_reports(
        run_config,
        generation_result,
        resolved_libraries,
    )
    write_json(output_dir / "evaluation_report.json", evaluation_report)
    write_json(output_dir / "enforcement_report.json", enforcement_report)
    write_json(output_dir / "run_summary.json", run_summary)

    print(f"final status: {run_summary['final_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
