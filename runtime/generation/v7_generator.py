from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.mode_system.mode_selection_engine import select_mode
from runtime.validation.validator_engine import evaluate_text
from runtime.validation.mode_alignment_validator import evaluate_mode_alignment
from runtime.validation.dual_lane_validator import evaluate_dual_lane
from runtime.validation.pillar_coverage_validator import evaluate_pillar_coverage
from runtime.validation.heo_override_validator import evaluate_heo_override
from runtime.validation.voice_consistency_validator import evaluate_voice_consistency
from runtime.validation.style_drift_detector import evaluate_style_drift
from runtime.validation.human_likeness_validator import evaluate_human_likeness
from runtime.validation.grit_appropriateness_validator import evaluate_grit_appropriateness
from runtime.validation.phrase_repetition_validator import evaluate_phrase_repetition
from runtime.validation.rhetorical_frame_repetition_validator import evaluate_rhetorical_frame_repetition
from runtime.validation.metaphor_overuse_validator import evaluate_metaphor_overuse
from runtime.validation.grit_phrase_reuse_validator import evaluate_grit_phrase_reuse
from runtime.validation.lexical_grounding_validator import evaluate_lexical_grounding
from runtime.validation.cadence_validator import evaluate_cadence
from runtime.validation.thought_visibility_validator import evaluate_thought_visibility
from runtime.grit_system.grit_selector import select_grit
from runtime.voice_system.voice_runtime import (
    load_voice_profile,
    load_vocabulary_profile,
    enforce_voice_identity,
    enforce_lexical_grounding,
)
from runtime.phrase_system.phrase_runtime import apply_phrase_controls


REGISTRY_PATH = ROOT / "runtime" / "validation" / "validator_registry.json"
THRESHOLDS_PATH = ROOT / "runtime" / "validation" / "evaluation_thresholds.json"
PATTERN_REGISTRY_PATH = ROOT / "runtime" / "pattern_system" / "story_authority_patterns.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def select_opening_pattern(profile: dict, mode_id: str, grit_level: str) -> dict:
    registry = load_json(PATTERN_REGISTRY_PATH)
    intent_blob = " ".join(
        str(profile.get(key, "")).lower()
        for key in ["desired_reader_impact", "desired_viral_profile", "genre", "topic", "prompt_brief"]
    )
    intent_map = {
        "resonance": ["resonance", "memory", "story", "emotion", "reflect"],
        "reflection": ["reflection", "reflect", "insight"],
        "memory": ["memory", "remember", "scene"],
        "credibility": ["trust", "credible", "credibility"],
        "explanation": ["explain", "why", "understand"],
        "clarity": ["clarity", "guide", "steps", "plain"],
        "story": ["story", "scene", "narrative"],
        "stakes": ["stakes", "risk", "pressure"],
        "trust": ["trust", "evidence", "record"],
        "correction": ["correction", "wrong", "mistake"],
        "truth_callout": ["self-deception", "avoidance", "truth", "callout"],
        "reframe": ["reframe", "not confusion", "not complexity"],
        "teaching": ["teach", "lesson", "guide"],
        "pattern_recognition": ["pattern", "repeat", "keeps disguising"],
        "meaning": ["meaning", "what matters", "insight"],
    }
    active_intents = {
        intent
        for intent, tokens in intent_map.items()
        if any(token in intent_blob for token in tokens)
    } or {"meaning"}
    recent_patterns = profile.get("recent_patterns", [])
    recent_pattern_counts = profile.get("recent_pattern_counts", {})
    candidates = []
    for pattern in registry["patterns"]:
        if mode_id not in pattern["supported_modes"]:
            continue
        if grit_level not in pattern["grit_compatible"]:
            continue
        intent_overlap = len(active_intents & set(pattern["supported_intents"]))
        penalty = 0.0
        if pattern["pattern_id"] in recent_patterns:
            penalty += registry["pattern_cooldown"]["previous_draft_penalty"]
        if recent_pattern_counts.get(pattern["pattern_id"], 0) > registry["pattern_cooldown"]["max_repeat_before_penalty"]:
            penalty += 0.2 * recent_pattern_counts.get(pattern["pattern_id"], 0)
        selection_score = round((intent_overlap * 0.35) + 1.0 - penalty, 3)
        candidates.append((selection_score, pattern))
    selected_score, selected = sorted(candidates, key=lambda item: (-item[0], item[1]["pattern_id"]))[0]
    return {
        "pattern_id": selected["pattern_id"],
        "selection_score": selected_score,
        "supported_intents_matched": sorted(active_intents & set(selected["supported_intents"])),
        "structure": selected["structure"],
        "voice_requirements": selected["voice_requirements"],
        "opening_function": selected["opening_function"],
        "pattern_cooldown_applied": selected["pattern_id"] in recent_patterns or recent_pattern_counts.get(selected["pattern_id"], 0) > 1,
        "recent_patterns": recent_patterns,
        "recent_pattern_counts": recent_pattern_counts,
    }


def build_pattern_opening(profile: dict, mode_id: str, grit_context: dict, pattern_context: dict) -> str:
    audience = profile.get("audience", "general readers")
    topic = profile.get("topic", "the truth people keep refusing to name")
    grit_phrase = grit_opening(grit_context, mode_id)
    if pattern_context["pattern_id"] == "personal_to_insight":
        return (
            f"{grit_phrase} I have learned that a person can live beside the truth for a long time before they let it touch their name. "
            f"For {audience}, {topic} begins there, in the moment private knowledge becomes usable insight."
        )
    if pattern_context["pattern_id"] == "observation_to_authority":
        return (
            f"{grit_phrase} The visible pattern is usually simpler than the excuse built around it. "
            f"For {audience}, {topic} becomes credible the moment the record and the behavior stop pointing in different directions."
        )
    if pattern_context["pattern_id"] == "narrative_hook_to_credibility":
        return (
            f"{grit_phrase} Some truths announce themselves first as a scene: a room gone quiet, a record set on the table, a face that cannot keep pretending. "
            f"That is where {topic} earns the right to mean something for {audience}."
        )
    if pattern_context["pattern_id"] == "correction_based_opening":
        return (
            f"{grit_phrase} This is not a complexity problem. It is a truth problem wearing a more respectable coat. "
            f"For {audience}, {topic} has to be named that plainly before anything honest can follow."
        )
    return (
        f"{grit_phrase} The lesson usually arrives before the language for it does. "
        f"For {audience}, {topic} becomes useful when lived experience is allowed to harden into a pattern without turning into jargon."
    )


def grit_opening(grit_context: dict, mode_id: str) -> str:
    phrase = grit_context["selected_grit_phrase"]
    if mode_id == "utility" and grit_context["grit_level"] in {"high", "extreme"}:
        return "You are going in circles, and some part of you already knows why."
    return phrase


def build_candidates(profile: dict, mode_id: str, grit_context: dict) -> list[dict]:
    topic = profile.get("topic", "a concrete detail that changes what people think is true")
    audience = profile.get("audience", "general readers")
    platform = profile.get("target_platform", "linkedin")
    voice_profile = load_voice_profile()
    mode_rules = voice_profile["mode_expression_rules"].get(mode_id, voice_profile["mode_expression_rules"]["hybrid"])
    grit_level = grit_context["grit_level"]
    pattern_context = select_opening_pattern(profile, mode_id, grit_level)
    opening = build_pattern_opening(profile, mode_id, grit_context, pattern_context)
    if mode_id == "utility":
        aligned_text = (
            f"{opening}\n\n"
            f"For {audience}, that means starting with the record itself and naming the step that can be checked.\n\n"
            f"What matters here is plain witness. A screenshot becomes believable when the time stamp, route, and source line up in the same light. "
            f"So {topic} can be explained without drama and still carry weight on {platform}."
        )
    elif mode_id == "narrative":
        aligned_text = (
            f"{opening}\n\n"
            f"For {audience}, this begins the way memory begins: with a record, a route, and a name that finally stand still together.\n\n"
            f"So {topic} matters to me as more than an argument. It feels like a lantern carried through weather, small but steady enough for other people to see what has been there all along and carry it with them onto {platform}."
        )
    elif mode_id == "authority":
        aligned_text = (
            f"{opening}\n\n"
            f"For {audience}, the task is to name the record, the route, and the discrepancy without performance.\n\n"
            f"For that reason, {topic} is not just a claim. It is a judgment shaped by evidence and carried in plain English, the kind other people can test for themselves before they repeat it on {platform}."
        )
    else:
        aligned_text = (
            f"{opening}\n\n"
            f"In this piece for {audience}, the pressure comes from a record, a route, and a name that finally line up in public.\n\n"
            f"That example matters because it turns {topic} from opinion into something other people can verify, carry, and discuss on {platform} without losing its meaning."
        )
    candidate_text, phrase_controls = apply_phrase_controls(aligned_text, mode_id, grit_level)
    fallback_text = (
        "You are closer than you think. Trust the process, keep moving, and everything will change. "
        "What matters is mindset, energy, and the courage to believe in yourself even when other people do not."
    )
    fallback_pattern_context = {
        "pattern_id": "generic_fallback_nonpattern",
        "selection_score": 0.0,
        "supported_intents_matched": [],
        "structure": ["generic_motivation"],
        "voice_requirements": [],
        "opening_function": "negative control",
        "pattern_cooldown_applied": False,
        "recent_patterns": [],
        "recent_pattern_counts": {}
    }
    return [
        {
            "candidate_id": "v7_candidate_001",
            "text": candidate_text,
            "voice_expression": mode_rules["emphasis"],
            "grit_level": grit_level,
            "grit_context": grit_context,
            "pattern_context": pattern_context,
            "phrase_controls": phrase_controls,
        },
        {
            "candidate_id": "v7_candidate_002",
            "text": fallback_text,
            "voice_expression": ["generic_motivation", "marketer_drift"],
            "grit_level": "medium",
            "grit_context": {
                "grit_level": "medium",
                "selected_grit_phrase": "You are closer than you think.",
                "grit_cooldown_applied": False,
                "cooled_down_phrases": [],
                "recent_grit_phrases": [],
                "recent_grit_phrase_counts": {}
            },
            "pattern_context": fallback_pattern_context,
            "phrase_controls": apply_phrase_controls(fallback_text, mode_id, "medium")[1],
        },
    ]


def evaluate_candidate(profile: dict, candidate: dict) -> dict:
    validator_registry = load_json(REGISTRY_PATH)
    thresholds = load_json(THRESHOLDS_PATH)
    mode_selection = select_mode(profile)
    mode_id = mode_selection["mode_id"]
    voice_profile = load_voice_profile()
    vocabulary_profile = load_vocabulary_profile()
    grit_context = candidate.get("grit_context") or select_grit(
        {
            "mode": mode_id,
            "requested_grit_level": profile.get("requested_grit_level"),
            "emotional_fragility": profile.get("emotional_fragility"),
            "sensitive_topic": profile.get("sensitive_topic", False),
            "self_deception_detected": profile.get("self_deception_detected", False),
            "clear_avoidance_detected": profile.get("clear_avoidance_detected", False),
            "recent_grit_phrases": profile.get("recent_grit_phrases", []),
            "recent_grit_phrase_counts": profile.get("recent_grit_phrase_counts", {}),
            "current_draft_grit_phrases": profile.get("current_draft_grit_phrases", []),
        },
        voice_profile,
    )
    pre_validation_text = enforce_voice_identity(candidate["text"], voice_profile, mode_id, final_pass=False)
    pre_validation_text = enforce_lexical_grounding(pre_validation_text, vocabulary_profile, profile)
    pre_validation_text, phrase_controls = apply_phrase_controls(
        pre_validation_text,
        mode_id,
        candidate.get("grit_level", grit_context["grit_level"]),
    )
    base_report = evaluate_text(pre_validation_text, {}, thresholds, validator_registry)
    mode_result = evaluate_mode_alignment(mode_selection, base_report)
    dual_lane_result = evaluate_dual_lane(load_json(ROOT / "runtime" / "pillar_weighting" / "weighting_profiles.json"), base_report)
    pillar_result = evaluate_pillar_coverage(mode_selection, base_report)
    heo_result = evaluate_heo_override(base_report)
    reinforced_text = enforce_voice_identity(pre_validation_text, voice_profile, mode_id, final_pass=True)
    reinforced_text = enforce_lexical_grounding(reinforced_text, vocabulary_profile, profile)
    reinforced_text, final_phrase_controls = apply_phrase_controls(
        reinforced_text,
        mode_id,
        candidate.get("grit_level", grit_context["grit_level"]),
    )
    final_report = evaluate_text(reinforced_text, {}, thresholds, validator_registry)
    mode_result = evaluate_mode_alignment(mode_selection, final_report)
    dual_lane_result = evaluate_dual_lane(load_json(ROOT / "runtime" / "pillar_weighting" / "weighting_profiles.json"), final_report)
    pillar_result = evaluate_pillar_coverage(mode_selection, final_report)
    heo_result = evaluate_heo_override(final_report)
    voice_result = evaluate_voice_consistency(reinforced_text, mode_id)
    drift_result = evaluate_style_drift(reinforced_text, mode_id)
    human_voice_result = evaluate_human_likeness(reinforced_text, mode_id)
    grit_result = evaluate_grit_appropriateness(grit_context, profile)
    phrase_result = evaluate_phrase_repetition(reinforced_text, candidate.get("grit_level", grit_context["grit_level"]))
    rhetorical_result = evaluate_rhetorical_frame_repetition(reinforced_text, candidate.get("grit_level", grit_context["grit_level"]))
    metaphor_result = evaluate_metaphor_overuse(reinforced_text, candidate.get("grit_level", grit_context["grit_level"]))
    grit_phrase_result = evaluate_grit_phrase_reuse(reinforced_text, candidate.get("grit_level", grit_context["grit_level"]))
    lexical_result = evaluate_lexical_grounding(reinforced_text, mode_id, profile)
    cadence_result = evaluate_cadence(reinforced_text)
    thought_visibility_result = evaluate_thought_visibility(reinforced_text)

    final_report["validator_results"] = final_report["validator_results"] + [
        mode_result,
        dual_lane_result,
        pillar_result,
        heo_result,
        voice_result,
        drift_result,
        human_voice_result,
        grit_result,
        phrase_result,
        rhetorical_result,
        metaphor_result,
        grit_phrase_result,
        lexical_result,
        cadence_result,
        thought_visibility_result,
    ]
    return {
        "candidate_id": candidate["candidate_id"],
        "draft_text": reinforced_text,
        "mode_selection": mode_selection,
        "v7_results": {
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
            "cadence_validator": cadence_result,
            "thought_visibility_validator": thought_visibility_result,
        },
        "evaluation_report_compatible": {
            "validator_results": final_report["validator_results"],
            "mode_context": mode_selection,
            "pillar_weighting_context": mode_selection["weighting_profile"],
            "v7_1_voice_context": {
                "voice_id": voice_profile["voice_id"],
                "mode_expression": candidate.get("voice_expression", []),
                "mode_id": mode_id,
            },
            "v7_2_grit_context": grit_context,
            "v7_3_phrase_context": final_phrase_controls,
            "v7_4_pattern_context": candidate.get("pattern_context", {}),
            "lexical_alignment_score": lexical_result["evidence"]["lexical_alignment_score"],
            "abstract_word_ratio": lexical_result["evidence"]["abstract_word_ratio"],
            "flagged_terms": lexical_result["evidence"]["flagged_terms"],
            "cadence_naturalness_score": cadence_result["evidence"]["cadence_naturalness_score"],
            "development_depth_score": cadence_result["evidence"]["development_depth_score"],
            "compression_score": cadence_result["evidence"]["compression_score"],
            "compression_flags": cadence_result["evidence"]["compression_flags"],
            "roughness_score": thought_visibility_result["evidence"]["roughness_score"],
            "over_polish_flags": thought_visibility_result["evidence"]["over_polish_flags"],
            "tension_presence_score": thought_visibility_result["evidence"]["tension_presence_score"],
            "thought_visibility_score": thought_visibility_result["evidence"]["thought_visibility_score"],
            "experiential_depth_score": thought_visibility_result["evidence"]["experiential_depth_score"],
            "process_visibility_score": thought_visibility_result["evidence"]["process_visibility_score"],
            "experience_presence_score": thought_visibility_result["evidence"]["experience_presence_score"],
            "summarization_flags": thought_visibility_result["evidence"]["summarization_flags"],
        },
    }


def run_generation(profile: dict) -> dict:
    resolved_mode = select_mode(profile)["mode_id"]
    grit_context = select_grit(
        {
            "mode": resolved_mode,
            "requested_grit_level": profile.get("requested_grit_level"),
            "emotional_fragility": profile.get("emotional_fragility"),
            "sensitive_topic": profile.get("sensitive_topic", False),
            "self_deception_detected": profile.get("self_deception_detected", False),
            "clear_avoidance_detected": profile.get("clear_avoidance_detected", False),
            "recent_grit_phrases": profile.get("recent_grit_phrases", []),
            "recent_grit_phrase_counts": profile.get("recent_grit_phrase_counts", {}),
            "current_draft_grit_phrases": profile.get("current_draft_grit_phrases", []),
        },
        load_voice_profile(),
    )
    candidates = [evaluate_candidate(profile, candidate) for candidate in build_candidates(profile, resolved_mode, grit_context)]
    selected = sorted(
        candidates,
        key=lambda item: (
            item["v7_results"]["heo_override_validator"]["status"] != "fail",
            item["v7_results"]["thought_visibility_validator"]["score"],
            item["v7_results"]["cadence_validator"]["score"],
            item["v7_results"]["pillar_coverage_validator"]["score"],
            item["v7_results"]["mode_alignment_validator"]["score"],
        ),
        reverse=True,
    )[0]
    return {
        "profile": profile,
        "selected_candidate_id": selected["candidate_id"],
        "selected_output": selected["draft_text"],
        "mode_selection": selected["mode_selection"],
        "v7_results": selected["v7_results"],
        "evaluation_report_compatible": selected["evaluation_report_compatible"],
        "all_candidates": candidates,
    }


if __name__ == "__main__":
    sample = {
        "mode": "hybrid",
        "genre": "essayistic_long_form_post",
        "audience": "general intelligent internet readers",
        "target_platform": "linkedin",
        "topic": "how one concrete record can break a larger public lie",
    }
    print(json.dumps(run_generation(sample), indent=2))
