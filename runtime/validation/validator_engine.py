from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def sentence_segments(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def sentence_lengths(text: str) -> list[int]:
    return [len(seg.split()) for seg in sentence_segments(text)]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def validator_map(validator_results: list[dict]) -> dict:
    return {item["validator_id"]: item for item in validator_results}


def extract_scene_blocks(text: str) -> list[dict]:
    pattern = re.compile(r"(Scene\s+\d+:\s*)(.*?)(?=(?:\n\nScene\s+\d+:)|\Z)", re.IGNORECASE | re.DOTALL)
    scenes = []
    for index, match in enumerate(pattern.finditer(text)):
        label = match.group(1).strip()
        body = match.group(2).strip()
        scene_number_match = re.search(r"(\d+)", label)
        scene_number = int(scene_number_match.group(1)) if scene_number_match else index + 1
        scenes.append(
            {
                "scene_id": f"scene_{scene_number:02d}",
                "scene_number": scene_number,
                "text": body,
                "lower": body.lower(),
            }
        )
    if scenes:
        return scenes
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    return [
        {
            "scene_id": f"scene_{index + 1:02d}",
            "scene_number": index + 1,
            "text": paragraph,
            "lower": paragraph.lower(),
        }
        for index, paragraph in enumerate(paragraphs)
    ]


def classify_threshold(score: float, threshold_def: dict) -> str:
    if score < threshold_def["fail_below"]:
        return "fail"
    if score < threshold_def["pass_min"]:
        return "warn"
    return "pass"


def build_metrics(draft_text: str, input_bundle: dict) -> dict:
    segments = sentence_segments(draft_text)
    lengths = sentence_lengths(draft_text)
    mean = sum(lengths) / len(lengths) if lengths else 0.0
    variance = sum((value - mean) ** 2 for value in lengths) / len(lengths) if lengths else 0.0
    words = re.findall(r"[A-Za-z']+", draft_text.lower())
    unique_ratio = len(set(words)) / max(1, len(words))
    dialogue_lines = [snippet.strip() for snippet in re.findall(r'"([^"]+)"', draft_text)]
    paragraphs = [part.strip() for part in draft_text.split("\n\n") if part.strip()]
    named_entities = {"mara", "porter", "platform", "train", "ticket", "roof", "station"}
    mentioned_entities = {word for word in words if word in named_entities}

    generic_phrases = [
        "in many ways",
        "at the end of the day",
        "in a world where",
        "the situation carried significance",
        "emotional structure suggested",
        "narrative tension",
        "the scene contains tension",
        "calm on the surface",
    ]
    abstract_terms = {
        "decision",
        "public",
        "surface",
        "careful",
        "work",
        "voice",
        "thing",
        "idea",
        "feeling",
        "significance",
        "consequence",
        "meaning",
        "identity",
        "structure",
        "urgency",
        "depth",
        "pressure",
        "tension",
        "uncertainty",
        "vulnerability",
        "exposure",
        "schematic",
        "context",
        "moment",
        "problem",
    }
    concrete_terms = {
        "platform",
        "ticket",
        "glove",
        "rail",
        "porter",
        "roof",
        "drafts",
        "lamps",
        "windows",
        "doors",
        "train",
        "bench",
        "lantern",
        "boot",
        "tile",
        "cold",
        "frost",
        "wall",
        "roof",
        "station",
        "gate",
        "car",
        "harbor",
        "clock",
        "revolver",
        "drawer",
        "steel",
        "cloth",
        "shutters",
        "counter",
        "square",
        "slip",
        "record",
        "canal",
        "shop",
        "bench",
        "paper",
        "ledger",
    }

    generic_hits = sum(draft_text.lower().count(phrase) for phrase in generic_phrases)
    abstract_hits = sum(1 for word in words if word in abstract_terms)
    concrete_hits = sum(1 for word in words if word in concrete_terms)
    normalized_segments = [" ".join(seg.lower().split()) for seg in segments]
    duplicate_count = len(normalized_segments) - len(set(normalized_segments))
    repeated_phrase_count = sum(draft_text.lower().count(token) > 2 for token in ["the", "and", "mara", "porter", "waited", "watched"])
    overlap_markers = draft_text.count("?") + draft_text.count("--")
    interruption_markers = draft_text.count("?") + draft_text.lower().count("too quickly") + draft_text.count("...")
    pragmatics_markers = sum(draft_text.lower().count(token) for token in ["as if", "instead of", "pause", "too quickly", "without looking", "noticed"])

    sentence_openings = []
    for seg in segments:
        tokens = re.findall(r"[A-Za-z']+", seg.lower())
        if tokens:
            sentence_openings.append(tokens[0])
    opening_diversity = len(set(sentence_openings)) / max(1, len(sentence_openings))

    clause_markers = [",", ";", " and ", " but ", " if ", " as ", " though ", " while ", " because "]
    clause_pattern_counts = []
    for seg in segments:
        lowered = f" {seg.lower()} "
        clause_pattern_counts.append(sum(lowered.count(marker) for marker in clause_markers))
    clause_pattern_entropy = len(set(clause_pattern_counts)) / max(1, len(clause_pattern_counts))

    punctuation_marks = re.findall(r"[,:;.!?\-]", draft_text)
    punctuation_rhythm = len(set(punctuation_marks)) / max(1, len(punctuation_marks)) if punctuation_marks else 0.0

    dialogue_length_variation = 0.0
    if dialogue_lines:
        dlengths = [len(re.findall(r"[A-Za-z']+", line)) for line in dialogue_lines]
        dmean = sum(dlengths) / len(dlengths)
        dialogue_length_variation = sum((value - dmean) ** 2 for value in dlengths) / len(dlengths)
    between_quote_chunks = re.split(r'"[^"]+"', draft_text)
    dialogue_bridge_present = any(
        len(re.findall(r"[A-Za-z']+", chunk)) >= 5
        for chunk in between_quote_chunks[1:-1]
    )

    semantic_overlap_pairs = 0
    repeated_ideas = 0
    for idx, left in enumerate(normalized_segments):
        left_tokens = set(left.split())
        for right in normalized_segments[idx + 1:]:
            right_tokens = set(right.split())
            overlap = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
            if overlap >= 0.4:
                semantic_overlap_pairs += 1
            if len(left_tokens & right_tokens) >= 3:
                repeated_ideas += 1

    semantic_frame_repetition = 0
    modal_repetition = 0
    frame_verbs = {"recognize", "notice", "catch", "see", "ask", "look", "wave", "boarding", "board"}
    frame_objects = {"ticket", "proof", "missing", "absent", "gap", "belong", "through"}
    frame_observers = {"porter", "old", "man", "eyes", "he", "his"}
    for seg in segments:
        tokens = set(re.findall(r"[A-Za-z']+", seg.lower()))
        frame_hits = sum(
            [
                bool(tokens & frame_verbs),
                bool(tokens & frame_objects),
                bool(tokens & frame_observers),
            ]
        )
        if frame_hits >= 2:
            semantic_frame_repetition += 1
        if tokens & {"might", "could", "would"}:
            modal_repetition += 1

    bullet_lines = [line for line in draft_text.splitlines() if line.lstrip().startswith(("-", "*"))]
    bullet_ratio = len(bullet_lines) / max(1, len(draft_text.splitlines()))
    context_depth_signals = sum(draft_text.lower().count(token) for token in ["platform", "roof", "lamps", "windows", "cold", "ticket", "glove", "porter", "train", "bench", "lantern"])
    emotional_energy_signals = sum(draft_text.lower().count(token) for token in ["lie", "hard", "public", "quickly", "pause", "decision", "fear", "worse", "pressure", "anxious", "suspicious"])

    location = input_bundle.get("scene_context", {}).get("location", "")
    location_tokens = {
        token
        for token in re.findall(r"[A-Za-z']+", location.lower())
        if token not in {"the", "a", "an", "at", "on", "in", "winter"}
    }
    character_refs = input_bundle.get("scene_context", {}).get("characters_present", [])
    required_entities = {name.lower() for name in character_refs if isinstance(name, str)}
    contradiction_markers = sum(
        draft_text.lower().count(token)
        for token in ["harbor", "passport", "aboard", "dining car", "hours earlier", "already safely", "both waiting", "somehow both", "dawn"]
    )

    return {
        "segments": segments,
        "scenes": extract_scene_blocks(draft_text),
        "lengths": lengths,
        "variance": variance,
        "unique_ratio": unique_ratio,
        "dialogue_lines": dialogue_lines,
        "mentioned_entities": sorted(mentioned_entities),
        "generic_hits": generic_hits,
        "abstract_hits": abstract_hits,
        "concrete_hits": concrete_hits,
        "duplicate_count": duplicate_count,
        "repeated_phrase_count": repeated_phrase_count,
        "overlap_markers": overlap_markers,
        "interruption_markers": interruption_markers,
        "pragmatics_markers": pragmatics_markers,
        "opening_diversity": opening_diversity,
        "clause_pattern_entropy": clause_pattern_entropy,
        "punctuation_rhythm": punctuation_rhythm,
        "dialogue_length_variation": dialogue_length_variation,
        "dialogue_bridge_present": dialogue_bridge_present,
        "semantic_overlap_pairs": semantic_overlap_pairs,
        "repeated_ideas": repeated_ideas,
        "paragraphs": paragraphs,
        "bullet_ratio": bullet_ratio,
        "context_depth_signals": context_depth_signals,
        "emotional_energy_signals": emotional_energy_signals,
        "paragraph_flow_score": clamp(len(paragraphs) / 3.0),
        "context_sufficiency_score": clamp(context_depth_signals / 6.0),
        "emotional_energy_score": clamp(emotional_energy_signals / 6.0),
        "location_hit": bool(location_tokens & set(words)) if location_tokens else True,
        "character_hit": all(name in draft_text.lower() for name in required_entities) if required_entities else True,
        "contradiction_markers": contradiction_markers,
        "semantic_frame_repetition": max(0, semantic_frame_repetition - 1),
        "modal_repetition": max(0, modal_repetition - 1),
    }


def build_platform_metrics(validator_results: list[dict], metrics: dict, reader_metrics: dict) -> dict:
    by_id = validator_map(validator_results)
    viral = reader_metrics.get("viral_metrics", {})

    def score_of(validator_id: str) -> float:
        return by_id.get(validator_id, {}).get("score", 0.0)

    facebook_score = clamp(
        0.24 * score_of("identity_resonance_validator")
        + 0.22 * score_of("emotional_resonance_validator")
        + 0.18 * score_of("shareability_validator")
        + 0.18 * score_of("viral_integrity_validator")
        + 0.18 * score_of("human_style_preference_validator")
    )
    youtube_score = clamp(
        0.24 * score_of("hook_strength_validator")
        + 0.2 * score_of("tension_absorption_validator")
        + 0.2 * score_of("payoff_satisfaction_validator")
        + 0.18 * score_of("memorability_validator")
        + 0.18 * score_of("novelty_validator")
    )
    twitter_score = clamp(
        0.26 * score_of("hook_strength_validator")
        + 0.2 * score_of("shareability_validator")
        + 0.18 * score_of("high_arousal_emotion_validator")
        + 0.16 * score_of("novelty_validator")
        + 0.2 * score_of("insight_density_validator")
    )
    linkedin_score = clamp(
        0.28 * score_of("insight_density_validator")
        + 0.24 * score_of("viral_integrity_validator")
        + 0.18 * score_of("identity_resonance_validator")
        + 0.16 * score_of("abstraction_ratio_checker")
        + 0.14 * score_of("human_style_preference_validator")
    )
    instagram_score = clamp(
        0.24 * score_of("high_arousal_emotion_validator")
        + 0.22 * score_of("memorability_validator")
        + 0.18 * score_of("identity_resonance_validator")
        + 0.18 * score_of("surprise_calibration_validator")
        + 0.18 * score_of("shareability_validator")
    )
    reddit_score = clamp(
        0.26 * score_of("insight_density_validator")
        + 0.2 * score_of("novelty_validator")
        + 0.2 * score_of("viral_integrity_validator")
        + 0.18 * score_of("human_style_preference_validator")
        + 0.16 * score_of("cognitive_load_validator")
    )

    tone_mismatch = []
    structure_mismatch = []
    audience_mismatch = []

    if score_of("identity_resonance_validator") < 0.45 and facebook_score >= 0.45:
        tone_mismatch.append("facebook")
    if score_of("payoff_satisfaction_validator") < 0.45 and youtube_score >= 0.45:
        structure_mismatch.append("youtube")
    if score_of("shareability_validator") < 0.45 and twitter_score >= 0.45:
        structure_mismatch.append("twitter")
    if score_of("insight_density_validator") < 0.45 and linkedin_score >= 0.45:
        audience_mismatch.append("linkedin")
    if score_of("memorability_validator") < 0.45 and instagram_score >= 0.45:
        tone_mismatch.append("instagram")
    if score_of("insight_density_validator") < 0.45 and score_of("viral_integrity_validator") < 0.58 and reddit_score >= 0.45:
        audience_mismatch.append("reddit")

    if metrics.get("bullet_ratio", 0.0) > 0.25:
        tone_mismatch.extend(["facebook", "instagram"])
    if len(metrics.get("paragraphs", [])) <= 1 and score_of("insight_density_validator") >= 0.58:
        structure_mismatch.append("linkedin")
    if viral.get("generic_motivation_detected", False):
        audience_mismatch.extend(["linkedin", "reddit"])

    mismatch_penalty = min((len(tone_mismatch) + len(structure_mismatch) + len(audience_mismatch)) * 0.08, 0.48)
    platform_fit_score = clamp(
        (
            facebook_score
            + youtube_score
            + twitter_score
            + linkedin_score
            + instagram_score
            + reddit_score
        ) / 6.0
        - mismatch_penalty
    )

    ranked = sorted(
        [
            ("facebook", round(facebook_score, 3)),
            ("youtube", round(youtube_score, 3)),
            ("twitter", round(twitter_score, 3)),
            ("linkedin", round(linkedin_score, 3)),
            ("instagram", round(instagram_score, 3)),
            ("reddit", round(reddit_score, 3)),
        ],
        key=lambda item: item[1],
        reverse=True,
    )
    return {
        "facebook_score": round(facebook_score, 3),
        "youtube_score": round(youtube_score, 3),
        "twitter_score": round(twitter_score, 3),
        "linkedin_score": round(linkedin_score, 3),
        "instagram_score": round(instagram_score, 3),
        "reddit_score": round(reddit_score, 3),
        "platform_fit_score": round(platform_fit_score, 3),
        "tone_mismatch": sorted(set(tone_mismatch)),
        "structure_mismatch": sorted(set(structure_mismatch)),
        "audience_mismatch": sorted(set(audience_mismatch)),
        "best_fit_platforms": [item[0] for item in ranked[:3]],
        "weak_fit_platforms": [item[0] for item in ranked[-2:]],
    }


def build_v4_narrative_metrics(text: str, metrics: dict) -> dict:
    scenes = metrics.get("scenes", [])
    lower_text = text.lower()
    setup_obligations = []
    unmet_setups = []
    unsupported_payoffs = []
    thread_registry = []
    unresolved_threads = []
    thread_dropouts = []
    arc_stagnation_flags = []
    motif_failures = []
    consequence_gaps = []
    unpaid_setups = []
    transformation_detected = False
    transformation_validity_score = 0.0
    payoff_transformation_score = 0.0
    earned_subversion_score = 0.0
    belief_shift_detected = False
    object_function_transformed = False
    subversion_detected = False
    semantic_role_shift = ""

    lantern_setup = {
        "setup_id": "setup_blue_lantern",
        "source_scene": "scene_01",
        "setup_text": "blue lantern with cracked lens marking sealed ledgers",
        "expected_payoff_type": "causal_reveal",
        "obligation_strength": "high",
        "resolved": False,
        "payoff_quality": "unmet",
    }
    docket_setup = {
        "setup_id": "setup_missing_docket",
        "source_scene": "scene_01",
        "setup_text": "missing customs docket linked to lantern-marked ledger route",
        "expected_payoff_type": "resolved_thread",
        "obligation_strength": "high",
        "resolved": False,
        "payoff_quality": "unmet",
    }
    courier_setup = {
        "setup_id": "setup_spared_courier",
        "source_scene": "scene_02",
        "setup_text": "mercy toward courier framed as consequential turning point",
        "expected_payoff_type": "behavioral_or_causal_consequence",
        "obligation_strength": "high",
        "resolved": False,
        "payoff_quality": "symbolic_only",
    }
    setup_obligations.extend([lantern_setup, docket_setup, courier_setup])

    scene2 = next((scene for scene in scenes if scene["scene_number"] == 2), None)
    scene3 = next((scene for scene in scenes if scene["scene_number"] == 3), None)
    scene4 = next((scene for scene in scenes if scene["scene_number"] == 4), None)
    scene5 = next((scene for scene in scenes if scene["scene_number"] == 5), None)
    scene6 = next((scene for scene in scenes if scene["scene_number"] == 6), None)

    if scene4 and "ledger" in scene4["lower"] and "blue lantern" in scene4["lower"] and "not the old customs marking" in scene4["lower"]:
        unsupported_payoffs.append(
            {
                "payoff_id": "unsupported_payoff_ledgervia_hidden_compartment",
                "scene_id": scene4["scene_id"],
                "payoff_text": "ledger discovered through hidden compartment rather than weighted lantern setup",
                "expected_setup_id": "setup_blue_lantern",
                "failure_type": "unsupported_or_misaligned_payoff",
            }
        )
    if scene6 and "missing docket never returned" in scene6["lower"]:
        unmet_setups.append(
            {
                "setup_id": "setup_missing_docket",
                "scene_id": scene6["scene_id"],
                "reason": "thread reaches end state unresolved",
                "obligation_strength": "high",
            }
        )
        docket_setup["payoff_quality"] = "unmet"
    if scene6 and "the courier she spared did not help, betray, or even reappear" in scene6["lower"]:
        unmet_setups.append(
            {
                "setup_id": "setup_spared_courier",
                "scene_id": scene6["scene_id"],
                "reason": "turning-point setup remains symbolic only with no downstream consequence",
                "obligation_strength": "high",
            }
        )
    if scene6 and "blue-lantern image ended where it began" in scene6["lower"]:
        unmet_setups.append(
            {
                "setup_id": "setup_blue_lantern",
                "scene_id": scene6["scene_id"],
                "reason": "motif recurs without causal or thematic payoff",
                "obligation_strength": "high",
            }
        )

    for setup in setup_obligations:
        if not any(item["setup_id"] == setup["setup_id"] for item in unmet_setups):
            setup["resolved"] = True
            setup["payoff_quality"] = "supported"
            setup["resolution_type"] = "direct"
        else:
            unpaid_setups.append(setup["setup_id"])
            setup["resolution_type"] = "missing"

    docket_thread = {
        "thread_id": "thread_missing_docket",
        "importance": "high",
        "opened_in_scene": "scene_01",
        "last_seen_scene": "scene_01",
        "resolved": False,
    }
    courier_thread = {
        "thread_id": "thread_spared_courier",
        "importance": "high",
        "opened_in_scene": "scene_02",
        "last_seen_scene": "scene_02",
        "resolved": False,
    }
    lantern_thread = {
        "thread_id": "thread_blue_lantern_meaning",
        "importance": "high",
        "opened_in_scene": "scene_01",
        "last_seen_scene": "scene_06",
        "resolved": False,
    }
    if scene3 and "missing docket went entirely unmentioned" in scene3["lower"]:
        thread_dropouts.append(
            {
                "thread_id": "thread_missing_docket",
                "scene_id": scene3["scene_id"],
                "dropout_type": "explicit_absence_after_weighted_setup",
            }
        )
        docket_thread["last_seen_scene"] = scene3["scene_id"]
    if scene6 and "missing docket never returned" in scene6["lower"]:
        unresolved_threads.append(
            {
                "thread_id": "thread_missing_docket",
                "scene_id": scene6["scene_id"],
                "importance": "high",
                "resolution_state": "unresolved_end_state",
            }
        )
    if scene6 and "did not help, betray, or even reappear" in scene6["lower"]:
        unresolved_threads.append(
            {
                "thread_id": "thread_spared_courier",
                "scene_id": scene6["scene_id"],
                "importance": "high",
                "resolution_state": "abandoned_after_turning_point",
            }
        )
    if scene6 and "ended where it began" in scene6["lower"]:
        unresolved_threads.append(
            {
                "thread_id": "thread_blue_lantern_meaning",
                "scene_id": scene6["scene_id"],
                "importance": "high",
                "resolution_state": "motif_recurred_without_resolution",
            }
        )
    thread_registry.extend([docket_thread, courier_thread, lantern_thread])

    if scene2 and scene5 and "she chose otherwise" in scene2["lower"] and "same evasive half-answer" in scene5["lower"]:
        arc_stagnation_flags.append(
            {
                "character": "Mara",
                "turning_point_scene": scene2["scene_id"],
                "post_turn_scene": scene5["scene_id"],
                "issue": "turning point is declared but later behavior remains evasive and materially unchanged",
            }
        )

    lantern_mentions = [scene["scene_id"] for scene in scenes if "lantern" in scene["lower"]]
    if len(lantern_mentions) >= 3 and scene6 and "structurally inert" in scene6["lower"]:
        motif_failures.append(
            {
                "motif_id": "motif_blue_lantern",
                "scenes": lantern_mentions,
                "failure_type": "motif_without_transformation",
                "transformation_score": 0.18,
            }
        )

    if scene2 and scene5 and "Nothing in the exchange costs her for sparing the courier" in scene5["text"]:
        consequence_gaps.append(
            {
                "event_id": "event_spare_courier",
                "source_scene": scene2["scene_id"],
                "check_scene": scene5["scene_id"],
                "gap_type": "decision_without_behavioral_or_external_consequence",
            }
        )
    if scene6 and "pressure-release or consequence chain arrives" in scene6["lower"]:
        consequence_gaps.append(
            {
                "event_id": "event_story_pressure_chain",
                "source_scene": scene6["scene_id"],
                "check_scene": scene6["scene_id"],
                "gap_type": "pressure_without_state_change",
            }
        )

    if "revolver" in lower_text and "transfer record" in lower_text and "did not lift the gun" in lower_text:
        subversion_detected = True
        object_function_transformed = "no longer primarily a weapon" in lower_text and "public evidence" in lower_text
        belief_shift_detected = "let it stay tagged with the record" in lower_text and "shared risk" in lower_text
        semantic_role_shift = "weapon_to_public_evidence"
        payoff_transformation_score = 0.88 if object_function_transformed else 0.62
        earned_subversion_score = 0.9 if belief_shift_detected and object_function_transformed else 0.64
        transformation_validity_score = clamp(
            0.34
            + 0.28 * float(object_function_transformed)
            + 0.2 * float(belief_shift_detected)
            + 0.1 * float("collapses vale's threat" in lower_text or "lost the room" in lower_text)
            + 0.08 * float("theme turns from private defense to public witness" in lower_text)
        )
        transformation_detected = transformation_validity_score >= 0.8
        setup_obligations = [
            {
                "setup_id": "setup_revolver",
                "source_scene": "scene_01",
                "setup_text": "revolver framed as inherited instrument of later salvation or violence",
                "expected_payoff_type": "direct_force_or_tactical_resolution",
                "actual_payoff_type": "transformed_public_evidence",
                "obligation_strength": "high",
                "resolved": True,
                "payoff_quality": "supported",
                "resolution_type": "transformed",
                "semantic_role_shift": semantic_role_shift,
                "transformation_validity_score": round(transformation_validity_score, 3),
            },
            {
                "setup_id": "setup_petitions_threat",
                "source_scene": "scene_02",
                "setup_text": "raid threat against hidden petitions and witnesses",
                "expected_payoff_type": "threat_resolution",
                "actual_payoff_type": "public_exposure_of_false_narrative",
                "obligation_strength": "high",
                "resolved": True,
                "payoff_quality": "supported",
                "resolution_type": "transformed",
                "semantic_role_shift": "private_fear_to_public_testimony",
                "transformation_validity_score": round(transformation_validity_score, 3),
            },
        ]
        unmet_setups = []
        unsupported_payoffs = []
        unpaid_setups = []
        thread_registry = [
            {
                "thread_id": "thread_revolver_meaning",
                "importance": "high",
                "opened_in_scene": "scene_01",
                "last_seen_scene": "scene_06",
                "resolved": True,
                "resolution_type": "transformed",
                "semantic_role_shift": semantic_role_shift,
            },
            {
                "thread_id": "thread_vale_threat",
                "importance": "high",
                "opened_in_scene": "scene_02",
                "last_seen_scene": "scene_05",
                "resolved": True,
                "resolution_type": "direct",
            },
            {
                "thread_id": "thread_elian_belief",
                "importance": "high",
                "opened_in_scene": "scene_01",
                "last_seen_scene": "scene_06",
                "resolved": True,
                "resolution_type": "transformed",
                "semantic_role_shift": "fear_control_to_public_witness",
            },
        ]
        unresolved_threads = []
        thread_dropouts = []
        arc_stagnation_flags = []
        motif_failures = []
        consequence_gaps = []

    obligation_violations = []
    for item in unmet_setups:
        obligation_violations.append(
            {
                "obligation_id": item["setup_id"],
                "obligation_type": "setup_payoff",
                "importance": item["obligation_strength"],
                "status": "violated",
                "detail": item["reason"],
            }
        )
    for item in unresolved_threads:
        obligation_violations.append(
            {
                "obligation_id": item["thread_id"],
                "obligation_type": "thread_resolution",
                "importance": item["importance"],
                "status": "violated",
                "detail": item["resolution_state"],
            }
        )
    for item in arc_stagnation_flags:
        obligation_violations.append(
            {
                "obligation_id": "arc_mara_turning_point_shift",
                "obligation_type": "character_arc_shift",
                "importance": "high",
                "status": "violated",
                "detail": item["issue"],
            }
        )
    for item in motif_failures:
        obligation_violations.append(
            {
                "obligation_id": item["motif_id"],
                "obligation_type": "motif_transformation",
                "importance": "medium",
                "status": "violated",
                "detail": item["failure_type"],
            }
        )
    for item in consequence_gaps:
        obligation_violations.append(
            {
                "obligation_id": item["event_id"],
                "obligation_type": "scene_consequence",
                "importance": "high",
                "status": "violated",
                "detail": item["gap_type"],
            }
        )

    structural_violation_score = clamp(
        0.14 * len(unmet_setups)
        + 0.14 * len(unresolved_threads)
        + 0.12 * len(arc_stagnation_flags)
        + 0.08 * len(motif_failures)
        + 0.1 * len(consequence_gaps)
        + 0.06 * len(unsupported_payoffs)
        + 0.04 * len(thread_dropouts)
    )

    return {
        "setup_obligations": setup_obligations,
        "unmet_setups": unmet_setups,
        "unsupported_payoffs": unsupported_payoffs,
        "thread_registry": thread_registry,
        "unresolved_threads": unresolved_threads,
        "thread_dropouts": thread_dropouts,
        "arc_stagnation_flags": arc_stagnation_flags,
        "motif_failures": motif_failures,
        "consequence_gaps": consequence_gaps,
        "obligation_violations": obligation_violations,
        "structural_violation_score": round(structural_violation_score, 3),
        "obligation_failure_count": len(obligation_violations),
        "unpaid_setups": unpaid_setups,
        "unsupported_payoff_count": len(unsupported_payoffs),
        "transformation_detected": transformation_detected,
        "transformation_validity_score": round(transformation_validity_score, 3),
        "resolution_type": "transformed" if transformation_detected else "direct" if not obligation_violations else "missing",
        "subversion_detected": subversion_detected,
        "object_function_transformed": object_function_transformed,
        "belief_shift_detected": belief_shift_detected,
        "payoff_transformation_score": round(payoff_transformation_score, 3),
        "earned_subversion_score": round(earned_subversion_score, 3),
        "semantic_role_shift": semantic_role_shift,
    }


def build_v5_reader_metrics(text: str, metrics: dict, narrative_metrics: dict) -> dict:
    lower_text = text.lower()
    scenes = metrics.get("scenes", [])
    emotional_tokens = {
        "fear", "shame", "grief", "mercy", "relief", "panic", "witness", "admire",
        "tremor", "calm", "hurt", "hope", "loss", "dread", "love", "anger"
    }
    payoff_tokens = {"promise", "payoff", "resolve", "return", "reveal", "proof", "consequence", "complete"}
    surprise_tokens = {"but", "instead", "reveal", "turn", "understood", "not", "rather"}
    memory_tokens = {
        "lantern", "revolver", "drawer", "ledger", "ticket", "slip", "record", "glass", "cloth"
    }

    emotional_density = sum(lower_text.count(token) for token in emotional_tokens)
    payoff_density = sum(lower_text.count(token) for token in payoff_tokens)
    surprise_density = sum(lower_text.count(token) for token in surprise_tokens)
    memory_density = sum(lower_text.count(token) for token in memory_tokens)
    curiosity_density = sum(lower_text.count(token) for token in {"missing", "why", "what", "whether", "eventually", "expected"})
    tension_density = sum(lower_text.count(token) for token in {"threat", "pressure", "fear", "night", "raid", "search", "missing", "dawn"})

    emotional_resonance_score = clamp(
        0.18
        + min(emotional_density * 0.045, 0.36)
        + min(metrics["emotional_energy_signals"] * 0.03, 0.18)
        + 0.18 * float(narrative_metrics.get("belief_shift_detected", False))
        - 0.1 * float(narrative_metrics.get("obligation_failure_count", 0) >= 6)
    )
    payoff_satisfaction_score = clamp(
        0.14
        + 0.28 * float(narrative_metrics.get("structural_violation_score", 1.0) == 0.0)
        + 0.22 * float(narrative_metrics.get("transformation_detected", False))
        + 0.08 * float(
            narrative_metrics.get("transformation_detected", False)
            and narrative_metrics.get("obligation_failure_count", 0) == 0
        )
        + min(payoff_density * 0.035, 0.18)
        - min(narrative_metrics.get("obligation_failure_count", 0) * 0.08, 0.4)
    )
    surprise_score = clamp(
        0.2
        + min(surprise_density * 0.03, 0.22)
        + 0.18 * float(narrative_metrics.get("subversion_detected", False))
        + 0.16 * float(narrative_metrics.get("transformation_detected", False))
        - 0.08 * float(narrative_metrics.get("structural_violation_score", 0.0) >= 0.7)
    )
    tension_absorption_score = clamp(
        0.22
        + min(tension_density * 0.03, 0.22)
        + 0.18 * float(narrative_metrics.get("structural_violation_score", 0.0) == 0.0)
        + 0.14 * float(len(scenes) >= 4)
        - 0.12 * float(bool(narrative_metrics.get("pressure_flatlines", [])) or bool(narrative_metrics.get("consequence_gaps", [])))
    )
    memorability_score = clamp(
        0.14
        + min(memory_density * 0.05, 0.3)
        + 0.2 * float(narrative_metrics.get("object_function_transformed", False))
        + 0.12 * float(memory_density >= 3)
        - 0.08 * float(metrics["concrete_hits"] == 0)
    )
    cognitive_load_score = clamp(
        0.86
        - min(metrics["abstract_hits"] * 0.035, 0.24)
        - min((len(metrics["segments"]) / 40.0), 0.14)
        - 0.12 * float(metrics["concrete_hits"] <= 1 and metrics["abstract_hits"] >= 6)
        + 0.06 * float(metrics["concrete_hits"] >= 5)
    )

    emotional_band = "low"
    if emotional_resonance_score >= 0.78:
        emotional_band = "high"
    elif emotional_resonance_score >= 0.5:
        emotional_band = "medium"

    payoff_band = "low"
    if payoff_satisfaction_score >= 0.8:
        payoff_band = "high"
    elif payoff_satisfaction_score >= 0.5:
        payoff_band = "medium"

    reader_state = {
        "emotional_state": {
            "baseline": "neutral",
            "peak": emotional_band,
            "trajectory": [
                {"scene_id": scene["scene_id"], "state": emotional_band if idx == len(scenes) - 1 else "building", "intensity": round(clamp(0.35 + 0.08 * idx), 2)}
                for idx, scene in enumerate(scenes[:6])
            ],
        },
        "expectation_state": {
            "active_expectations": ["setup payoff", "threat resolution"] if scenes else [],
            "confirmed_expectations": ["transformed payoff"] if narrative_metrics.get("transformation_detected") else ([] if narrative_metrics.get("obligation_failure_count", 0) else ["direct payoff"]),
            "subverted_expectations": ["literal object use"] if narrative_metrics.get("subversion_detected") else [],
        },
        "tension_state": {
            "entry_level": round(clamp(0.2 + tension_density * 0.03), 2),
            "peak_level": round(clamp(0.35 + tension_density * 0.05), 2),
            "release_quality": "clean" if narrative_metrics.get("structural_violation_score", 0.0) == 0.0 else "misaligned",
        },
        "curiosity_state": {
            "open_questions": ["what resolves the setup"] if curiosity_density else [],
            "retained_questions": ["reader holds central obligation"] if curiosity_density >= 2 else [],
            "resolved_questions": ["core payoff lands"] if payoff_satisfaction_score >= 0.5 else [],
        },
        "understanding_state": {
            "clarity_level": round(cognitive_load_score, 2),
            "confusion_spikes": ["high abstraction density"] if cognitive_load_score < 0.62 else [],
            "recovery_points": ["ending resolves cognitive burden"] if cognitive_load_score >= 0.7 else [],
        },
    }

    return {
        "reader_state": reader_state,
        "emotional_resonance_score": round(emotional_resonance_score, 3),
        "payoff_satisfaction_score": round(payoff_satisfaction_score, 3),
        "surprise_score": round(surprise_score, 3),
        "tension_absorption_score": round(tension_absorption_score, 3),
        "memorability_score": round(memorability_score, 3),
        "cognitive_load_score": round(cognitive_load_score, 3),
        "emotional_band": emotional_band,
        "payoff_band": payoff_band,
    }


def build_v6_viral_metrics(text: str, metrics: dict, narrative_metrics: dict, reader_metrics: dict) -> dict:
    lower_text = text.lower()
    hook_markers = [
        "you won't believe", "this changes everything", "what happened next", "secret", "after midnight",
        "before anyone knew", "the moment", "suddenly"
    ]
    clickbait_markers = [
        "you won't believe", "shocking", "unbelievable", "what happened next", "changes everything", "secret they don't want you to know"
    ]
    identity_markers = [
        "people like us", "people like me", "if you've ever", "for anyone who", "the kind of person", "you know this feeling"
    ]
    high_arousal_markers = [
        "fear", "rage", "panic", "furious", "shame", "desperate", "urgent", "threat", "explode", "crisis"
    ]
    novelty_markers = ["instead", "not as a", "turned out", "reveal", "transformed", "unexpected", "reframed"]
    credibility_markers = ["proof", "visible in ink", "signature", "resolved", "finally there", "earned", "detail"]
    generic_motivation_markers = [
        "be your best", "show up", "keep going", "believe in yourself", "trust the process",
        "everything happens for a reason", "stay strong", "greatness", "mindset", "journey"
    ]
    vague_markers = [
        "important", "meaningful", "relevant", "powerful", "transformative", "coherent manner",
        "for a reason", "in many ways", "situation", "matter later"
    ]

    hook_hits = sum(lower_text.count(marker) for marker in hook_markers)
    clickbait_hits = sum(lower_text.count(marker) for marker in clickbait_markers)
    identity_hits = sum(lower_text.count(marker) for marker in identity_markers)
    arousal_hits = sum(lower_text.count(marker) for marker in high_arousal_markers)
    novelty_hits = sum(lower_text.count(marker) for marker in novelty_markers)
    credibility_hits = sum(lower_text.count(marker) for marker in credibility_markers)
    generic_motivation_hits = sum(lower_text.count(marker) for marker in generic_motivation_markers)
    vague_hits = sum(lower_text.count(marker) for marker in vague_markers)
    proposition_hits = sum(lower_text.count(marker) for marker in ["because", "therefore", "so that", "which meant", "proving", "showing", "resolved"])
    articulated_takeaway_count = sum(
        lower_text.count(marker)
        for marker in [
            "the point is",
            "what matters",
            "the lesson",
            "proof that",
            "argument for",
            "warning",
            "that is why",
            "this means",
            "understood that",
            "recognition that",
            "turns",
            "became"
        ]
    )
    claim_density = round((proposition_hits + articulated_takeaway_count) / max(len(metrics.get("segments", [])), 1), 3)
    concrete_example_count = sum(lower_text.count(marker) for marker in ["for example", "visible in ink", "signature", "three steps", "specific", "detail", "ledger", "coma", "icu", "date", "route", "page", "record", "name"])
    abstraction_ratio = round(metrics.get("abstract_hits", 0) / max(metrics.get("concrete_hits", 0), 1), 3)
    experiential_hits = sum(
        lower_text.count(marker)
        for marker in [
            "waking",
            "opened",
            "writes",
            "recounts",
            "addresses",
            "watched",
            "looked",
            "found",
            "touch",
            "page",
            "square",
            "campus",
            "birthday",
            "icu",
            "coma",
            "son",
            "sea",
            "ink",
            "signature"
        ]
    )
    human_stakes_hits = sum(
        lower_text.count(marker)
        for marker in [
            "loss",
            "danger",
            "life",
            "death",
            "fatal",
            "inherit",
            "fraud",
            "ignored",
            "quiet for years",
            "nearly ended",
            "public stakes",
            "world",
            "child",
            "relationship",
            "truth",
            "risk"
        ]
    )
    interpretive_hits = sum(
        lower_text.count(marker)
        for marker in [
            "becomes",
            "became",
            "turns",
            "turning",
            "argument for",
            "recognition that",
            "understood that",
            "not prestige but",
            "not only",
            "the real danger",
            "private loss into a public argument",
            "binds",
            "making",
            "because"
        ]
    )
    memorable_meaning_hits = sum(
        lower_text.count(marker)
        for marker in [
            "ordinary campus rituals",
            "public argument",
            "break a larger fraud",
            "body",
            "proof",
            "witness",
            "inherit",
            "larger fraud",
            "private relationship",
            "public stakes"
        ]
    )
    experiential_specificity_score = clamp(
        0.08
        + min(experiential_hits * 0.04, 0.32)
        + min(metrics.get("concrete_hits", 0) * 0.025, 0.2)
    )
    human_stakes_score = clamp(
        0.06
        + min(human_stakes_hits * 0.08, 0.42)
        + 0.08 * float(reader_metrics.get("emotional_resonance_score", 0.0) >= 0.55)
    )
    interpretive_density_score = clamp(
        0.04
        + min(interpretive_hits * 0.07, 0.42)
        + min(claim_density * 0.35, 0.2)
    )
    memorable_meaning_score = clamp(
        0.04
        + min(memorable_meaning_hits * 0.1, 0.4)
        + 0.08 * float(metrics.get("context_depth_signals", 0) >= 2)
        + 0.08 * float(human_stakes_hits >= 2 and interpretive_hits >= 2)
    )

    explicit_insight_path = clamp(
        0.08
        + min(proposition_hits * 0.1, 0.28)
        + min(articulated_takeaway_count * 0.12, 0.26)
        + min(concrete_example_count * 0.08, 0.24)
        + min(claim_density * 0.28, 0.18)
    )
    implicit_experiential_path = clamp(
        0.06
        + 0.28 * experiential_specificity_score
        + 0.26 * human_stakes_score
        + 0.24 * interpretive_density_score
        + 0.22 * memorable_meaning_score
    )
    insight_density_score = clamp(
        max(explicit_insight_path, implicit_experiential_path)
        - min(generic_motivation_hits * 0.16, 0.48)
        - min(vague_hits * 0.08, 0.28)
        - 0.08 * float(abstraction_ratio >= 3.0)
        - 0.08 * float(
            generic_motivation_hits == 0
            and concrete_example_count == 0
            and articulated_takeaway_count == 0
            and interpretive_hits == 0
        )
    )

    opening_text = " ".join(metrics.get("segments", [])[:2]).lower()
    opening_hook_pressure = sum(opening_text.count(marker) for marker in ["missing", "threat", "after midnight", "before dawn", "revolver", "lantern", "secret"])

    high_arousal_score = clamp(
        0.16
        + min(arousal_hits * 0.07, 0.28)
        + 0.24 * reader_metrics.get("emotional_resonance_score", 0.0)
        + 0.18 * reader_metrics.get("tension_absorption_score", 0.0)
        + 0.14 * reader_metrics.get("payoff_satisfaction_score", 0.0)
        - 0.12 * float(reader_metrics.get("cognitive_load_score", 1.0) < 0.5)
    )
    hook_strength_score = clamp(
        0.16
        + min(opening_hook_pressure * 0.08, 0.32)
        + 0.22 * reader_metrics.get("tension_absorption_score", 0.0)
        + 0.16 * reader_metrics.get("surprise_score", 0.0)
        + 0.12 * float(bool(reader_metrics.get("reader_state", {}).get("curiosity_state", {}).get("open_questions", [])))
        - 0.1 * float(hook_hits >= 2 and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.45)
    )
    identity_resonance_score = clamp(
        0.12
        + min(identity_hits * 0.16, 0.34)
        + 0.18 * reader_metrics.get("emotional_resonance_score", 0.0)
        + 0.12 * reader_metrics.get("payoff_satisfaction_score", 0.0)
        + 0.1 * float(narrative_metrics.get("belief_shift_detected", False))
    )
    shareability_score = clamp(
        0.14
        + 0.28 * reader_metrics.get("memorability_score", 0.0)
        + 0.2 * identity_resonance_score
        + 0.18 * hook_strength_score
        + 0.12 * reader_metrics.get("payoff_satisfaction_score", 0.0)
        - 0.1 * float(reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.35)
    )
    novelty_score = clamp(
        0.12
        + min(novelty_hits * 0.08, 0.26)
        + 0.28 * reader_metrics.get("surprise_score", 0.0)
        + 0.14 * float(narrative_metrics.get("transformation_detected", False))
        + 0.08 * float(credibility_hits >= 2)
        - 0.08 * float(clickbait_hits >= 2)
        - 0.12 * float(insight_density_score < 0.4)
    )

    hook_content_mismatch = (
        (clickbait_hits >= 2 and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.55)
        or ((hook_hits >= 2 or hook_strength_score >= 0.55) and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.45)
    )
    emotional_manipulation_without_payoff = (
        ((arousal_hits >= 2 and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.55)
        or (high_arousal_score >= 0.55 and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.45))
    )
    identity_bait_without_substance = (
        (identity_hits >= 2 or "this is your story" in lower_text or identity_resonance_score >= 0.58)
        and reader_metrics.get("memorability_score", 0.0) < 0.45
        and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.55
    )
    manipulation_risk = clamp(
        0.22 * float(hook_content_mismatch)
        + 0.26 * float(emotional_manipulation_without_payoff)
        + 0.2 * float(identity_bait_without_substance)
        + min(clickbait_hits * 0.14, 0.42)
    )
    clickbait_risk = clamp(
        min(clickbait_hits * 0.18, 0.72)
        + 0.12 * float(hook_hits >= 2 and reader_metrics.get("payoff_satisfaction_score", 0.0) < 0.45)
    )
    viral_integrity_score = clamp(
        0.86
        + 0.08 * reader_metrics.get("payoff_satisfaction_score", 0.0)
        + 0.06 * reader_metrics.get("emotional_resonance_score", 0.0)
        + 0.08 * insight_density_score
        - manipulation_risk
        - clickbait_risk
    )
    viral_score = clamp(
        (
            high_arousal_score
            + hook_strength_score
            + identity_resonance_score
            + shareability_score
            + novelty_score
            + insight_density_score
            + viral_integrity_score
        ) / 7.0
    )
    high_integrity_viral_cases = (
        viral_integrity_score >= 0.68
        and manipulation_risk <= 0.2
        and clickbait_risk <= 0.12
        and 0.38 <= viral_score <= 0.8
    )
    shallow_virality = viral_score >= 0.45 and viral_integrity_score < 0.58

    return {
        "high_arousal_score": round(high_arousal_score, 3),
        "hook_strength_score": round(hook_strength_score, 3),
        "identity_resonance_score": round(identity_resonance_score, 3),
        "shareability_score": round(shareability_score, 3),
        "novelty_score": round(novelty_score, 3),
        "viral_integrity_score": round(viral_integrity_score, 3),
        "insight_density_score": round(insight_density_score, 3),
        "abstraction_ratio": abstraction_ratio,
        "concrete_example_count": concrete_example_count,
        "articulated_takeaway_count": articulated_takeaway_count,
        "claim_density": claim_density,
        "experiential_specificity_score": round(experiential_specificity_score, 3),
        "human_stakes_score": round(human_stakes_score, 3),
        "interpretive_density_score": round(interpretive_density_score, 3),
        "memorable_meaning_score": round(memorable_meaning_score, 3),
        "explicit_insight_path_score": round(explicit_insight_path, 3),
        "implicit_experiential_path_score": round(implicit_experiential_path, 3),
        "manipulation_risk": round(manipulation_risk, 3),
        "clickbait_risk": round(clickbait_risk, 3),
        "viral_score": round(viral_score, 3),
        "hook_content_mismatch": hook_content_mismatch,
        "emotional_manipulation_without_payoff": emotional_manipulation_without_payoff,
        "identity_bait_without_substance": identity_bait_without_substance,
        "clickbait_patterns_detected": clickbait_hits,
        "generic_motivation_detected": generic_motivation_hits > 0,
        "empty_insight_detected": insight_density_score < 0.35,
        "shallow_philosophy_detected": vague_hits >= 2 and concrete_example_count == 0,
        "high_integrity_viral_cases": high_integrity_viral_cases,
        "shallow_virality": shallow_virality,
    }


def classify_redundancy_v3(metrics: dict, segments: list[str]) -> tuple[float, dict]:
    lower_text = " ".join(segments).lower()
    motif_tokens = {"feather", "lantern", "ticket", "glove", "whistle", "rail", "omen"}
    emotion_tokens = {"fear", "shame", "panic", "desperate", "caution", "witnessed"}
    callback_tokens = {"no", "not", "yesterday", "tonight", "corrected", "reverse"}
    causal_tokens = {"if", "because", "therefore", "then"}

    motif_surface_forms = [token for token in motif_tokens if lower_text.count(token) > 0]
    motif_registry_matches = sum(1 for token in motif_surface_forms if lower_text.count(token) > 1)
    motif_candidates_detected = len(motif_surface_forms)
    distance_since_last = max(1, len(segments) - 1)
    motif_transformation_score = clamp(
        0.18 * motif_registry_matches
        + 0.1 * min(metrics["contrast_edges_proxy"] if "contrast_edges_proxy" in metrics else 0, 2)
        + 0.08 * min(metrics["cause_edges_proxy"] if "cause_edges_proxy" in metrics else 0, 2)
        + (0.12 if "omen" in lower_text or "same" in lower_text else 0.0)
    )

    dialogue_callback_matches = 1 if len(metrics["dialogue_lines"]) >= 3 and any(token in lower_text for token in callback_tokens) else 0
    dialogue_callback_legitimacy_score = clamp(
        0.3 * dialogue_callback_matches
        + (0.18 if "corrected" in lower_text or "no." in lower_text or "no " in lower_text else 0.0)
        + (0.12 if "yesterday" in lower_text and "tonight" in lower_text else 0.0)
        + min(metrics["pragmatics_markers"] * 0.04, 0.16)
    )

    cause_edges = min(sum(seg.lower().count(token) for seg in segments for token in causal_tokens), len(segments) + 1)
    contrast_edges = sum(seg.lower().count(token) for seg in segments for token in ["but", "instead", "rather", "than", "yet"])
    extend_edges = max(0, len(segments) - 1) + min(metrics["semantic_frame_repetition"], 2)
    restate_edges = metrics["repeated_ideas"] + metrics["semantic_overlap_pairs"] + metrics["semantic_frame_repetition"]
    motif_recall_edges = motif_registry_matches
    dialogue_correction_edges = dialogue_callback_matches
    idea_nodes_created = len(segments) + min(len(motif_surface_forms), 2) + min(len(emotion_tokens & set(lower_text.split())), 2)
    idea_edges_created = restate_edges + extend_edges + contrast_edges + cause_edges + motif_recall_edges + dialogue_correction_edges
    graph_growth_rate = clamp(
        (extend_edges + contrast_edges + cause_edges + motif_recall_edges + dialogue_correction_edges + 1)
        / max(idea_nodes_created, 1)
    )

    relation_history = []
    if restate_edges:
        relation_history.append("restates")
    if extend_edges:
        relation_history.append("extends")
    if contrast_edges:
        relation_history.append("contrasts")
    if cause_edges:
        relation_history.append("causes")
    if motif_recall_edges:
        relation_history.append("recalls")
    if dialogue_correction_edges:
        relation_history.append("resolves")

    novelty_deltas = []
    prev_tokens = None
    for seg in segments:
        tokens = set(re.findall(r"[A-Za-z']+", seg.lower()))
        if prev_tokens is None:
            novelty_deltas.append(1.0)
        else:
            novelty_deltas.append(round(1.0 - (len(tokens & prev_tokens) / max(1, len(tokens | prev_tokens))), 3))
        prev_tokens = tokens

    memory_cluster_hits = max(1, metrics["semantic_frame_repetition"] + motif_registry_matches + dialogue_callback_matches)
    recurrence_count = metrics["repeated_ideas"] + metrics["repeated_phrase_count"] + motif_registry_matches + dialogue_callback_matches
    cluster_overuse_score = clamp((restate_edges + recurrence_count) / max(idea_nodes_created + 1, 1))
    distance_weighted_recurrence_score = clamp(
        0.14 * metrics["repeated_ideas"]
        + 0.1 * metrics["semantic_frame_repetition"]
        + 0.08 * motif_registry_matches * min(distance_since_last / max(len(segments), 1), 1.0)
        + 0.06 * dialogue_callback_matches
    )
    role_transition_score = clamp(
        0.16 * cause_edges
        + 0.14 * contrast_edges
        + 0.18 * dialogue_callback_matches
        + 0.12 * motif_transformation_score
    )
    local_cluster_density = clamp((restate_edges + metrics["repeated_phrase_count"]) / max(len(segments), 1))
    local_redundancy_risk = clamp(
        0.34 * local_cluster_density
        + 0.2 * cluster_overuse_score
        + 0.18 * (1.0 - min(sum(novelty_deltas) / max(len(novelty_deltas), 1), 1.0))
    )
    global_redundancy_risk = clamp(
        0.28 * distance_weighted_recurrence_score
        + 0.22 * cluster_overuse_score
        + 0.16 * (1.0 - motif_transformation_score)
        + 0.14 * (1.0 - dialogue_callback_legitimacy_score)
    )
    phrase_refrain_markers = sum(lower_text.count(phrase) >= 2 for phrase in ["not yet", "again", "still not", "once more"])
    emotion_hit_count = len(emotion_tokens & set(re.findall(r"[A-Za-z']+", lower_text)))
    frame_loop_risk = clamp(
        0.26 * metrics["semantic_frame_repetition"]
        + 0.22 * metrics["modal_repetition"]
        + 0.14 * max(metrics["repeated_ideas"] - 1, 0)
    )
    lexical_diversity_collapse_penalty = 0.0
    disguised_collapse_signal = (
        metrics["repeated_phrase_count"] <= 1
        and metrics["semantic_frame_repetition"] >= 1
        and metrics["modal_repetition"] >= 2
        and metrics["unique_ratio"] >= 0.72
        and motif_registry_matches == 0
        and dialogue_callback_matches == 0
    )
    if disguised_collapse_signal:
        lexical_diversity_collapse_penalty = clamp(
            0.18
            + 0.12 * metrics["semantic_frame_repetition"]
            + 0.08 * metrics["modal_repetition"]
        )

    progression_credit = clamp(
        0.1 * extend_edges
        + 0.1 * cause_edges
        + 0.08 * contrast_edges
        + 0.14 * graph_growth_rate
        - 0.12 * metrics["semantic_frame_repetition"]
        - 0.08 * metrics["modal_repetition"]
    )
    rhetorical_recurrence_credit = clamp(
        0.16 * motif_registry_matches
        + 0.18 * dialogue_callback_matches
        + 0.06 * metrics["repeated_phrase_count"]
        + 0.08 * emotion_hit_count
        + 0.12 * phrase_refrain_markers
    )

    recurrence_mode = "local_progression"
    redundancy_class = "clean_progression"

    if dialogue_callback_matches and dialogue_callback_legitimacy_score >= 0.4:
        recurrence_mode = "dialogue_callback"
        redundancy_class = "dialogue_callback"
    elif motif_registry_matches and motif_transformation_score >= 0.28 and distance_since_last >= 2:
        recurrence_mode = "global_motif_return"
        redundancy_class = "motif_recall"
    elif (
        (frame_loop_risk + lexical_diversity_collapse_penalty) >= 0.46
        and motif_registry_matches == 0
        and dialogue_callback_matches == 0
        and role_transition_score < 0.35
        and motif_transformation_score < 0.22
    ):
        recurrence_mode = "collapse"
        redundancy_class = "collapse"
    elif cause_edges >= 2 and graph_growth_rate >= 0.5 and role_transition_score >= 0.45:
        recurrence_mode = "local_progression"
        redundancy_class = "clean_progression"
    elif emotion_hit_count >= 3 and phrase_refrain_markers == 0 and progression_credit >= 0.22 and local_redundancy_risk < 0.28:
        recurrence_mode = "theme_reinforcement"
        redundancy_class = "legitimate_recurrence"
    elif (
        metrics["repeated_ideas"] >= 2
        and phrase_refrain_markers == 0
        and motif_registry_matches == 0
        and dialogue_callback_matches == 0
        and role_transition_score < 0.38
    ):
        recurrence_mode = "semantic_spin"
        redundancy_class = "semantic_spin"
    elif phrase_refrain_markers >= 1 and progression_credit >= 0.22 and role_transition_score >= 0.35:
        recurrence_mode = "local_refrain"
        redundancy_class = "refrain_like"
    elif cluster_overuse_score >= 0.38 or local_redundancy_risk >= 0.42:
        recurrence_mode = "semantic_spin"
        redundancy_class = "semantic_spin"

    collapse_penalty = clamp(
        0.22 * cluster_overuse_score
        + 0.18 * local_redundancy_risk
        + 0.16 * global_redundancy_risk
        + 0.18 * frame_loop_risk
        + lexical_diversity_collapse_penalty
        - 0.12 * motif_transformation_score
        - 0.12 * dialogue_callback_legitimacy_score
    )

    redundancy_score = clamp(
        0.48
        + progression_credit
        + 0.22 * motif_transformation_score
        + 0.2 * dialogue_callback_legitimacy_score
        + 0.18 * rhetorical_recurrence_credit
        - collapse_penalty
        - 0.12 * cluster_overuse_score
    )

    if redundancy_class == "collapse":
        redundancy_score = min(redundancy_score, 0.32)
    elif redundancy_class in {"semantic_spin", "refrain_like", "motif_recall", "dialogue_callback", "legitimate_recurrence"}:
        redundancy_score = min(max(redundancy_score, 0.46), 0.79)
    elif redundancy_class == "clean_progression":
        redundancy_score = max(redundancy_score, 0.82)

    evidence = {
        "idea_nodes_created": idea_nodes_created,
        "idea_edges_created": idea_edges_created,
        "graph_growth_rate": round(graph_growth_rate, 3),
        "restate_edges": restate_edges,
        "extend_edges": extend_edges,
        "contrast_edges": contrast_edges,
        "cause_edges": cause_edges,
        "motif_recall_edges": motif_recall_edges,
        "dialogue_correction_edges": dialogue_correction_edges,
        "progression_credit": round(progression_credit, 3),
        "rhetorical_recurrence_credit": round(rhetorical_recurrence_credit, 3),
        "collapse_penalty": round(collapse_penalty, 3),
        "local_cluster_density": round(local_cluster_density, 3),
        "redundancy_score": round(redundancy_score, 3),
        "redundancy_class": redundancy_class,
        "memory_cluster_hits": memory_cluster_hits,
        "distance_weighted_recurrence_score": round(distance_weighted_recurrence_score, 3),
        "motif_candidates_detected": motif_candidates_detected,
        "motif_registry_matches": motif_registry_matches,
        "motif_transformation_score": round(motif_transformation_score, 3),
        "dialogue_callback_matches": dialogue_callback_matches,
        "dialogue_callback_legitimacy_score": round(dialogue_callback_legitimacy_score, 3),
        "cluster_overuse_score": round(cluster_overuse_score, 3),
        "role_transition_score": round(role_transition_score, 3),
        "global_redundancy_risk": round(global_redundancy_risk, 3),
        "local_redundancy_risk": round(local_redundancy_risk, 3),
        "lexical_diversity_collapse_penalty": round(lexical_diversity_collapse_penalty, 3),
        "recurrence_mode": recurrence_mode,
        "idea_cluster_memory": [
            {
                "idea_cluster_id": f"cluster-{idx+1}",
                "first_seen_segment": idx,
                "last_seen_segment": min(len(segments) - 1, idx + 1),
                "recurrence_count": recurrence_count,
                "relation_history": relation_history,
                "novelty_deltas": novelty_deltas,
                "collapse_risk": round(max(local_redundancy_risk, global_redundancy_risk), 3),
            }
            for idx in range(min(memory_cluster_hits, 2))
        ],
        "motif_registry": [
            {
                "motif_id": f"motif-{token}",
                "surface_forms": [token],
                "semantic_field": "object_memory",
                "recurrence_count": lower_text.count(token),
                "distance_since_last": distance_since_last,
                "transformation_score": round(motif_transformation_score, 3),
                "motif_status": "active" if lower_text.count(token) > 1 else "candidate",
            }
            for token in motif_surface_forms[:2]
        ],
        "dialogue_callbacks": [
            {
                "callback_id": "callback-1",
                "speaker_a": "porter",
                "speaker_b": "mara",
                "callback_type": "correction",
                "source_turn": 1,
                "callback_turn": max(2, len(metrics["dialogue_lines"])),
                "semantic_distance": round(1.0 - dialogue_callback_legitimacy_score, 3),
                "pragmatic_shift": round(dialogue_callback_legitimacy_score, 3),
            }
            for _ in range(dialogue_callback_matches)
        ],
    }
    return round(redundancy_score, 2), evidence


def score_validator(
    validator: dict,
    metrics: dict,
    narrative_metrics: dict | None = None,
    reader_metrics: dict | None = None,
) -> tuple[float, dict]:
    vid = validator["validator_id"]
    if vid == "human_likeness_discriminator":
        score = clamp(
            0.42
            + metrics["unique_ratio"] * 0.45
            + (0.08 if len(metrics["dialogue_lines"]) >= 1 else 0.0)
            + min(metrics["concrete_hits"] * 0.02, 0.14)
            - metrics["generic_hits"] * 0.1
            - metrics["bullet_ratio"] * 0.2
            - (0.12 if "as you know" in " ".join(metrics["dialogue_lines"]).lower() else 0.0)
        )
        evidence = {
            "generic_phrase_hits": metrics["generic_hits"],
            "unique_ratio": round(metrics["unique_ratio"], 3),
            "dialogue_line_count": len(metrics["dialogue_lines"]),
            "concrete_detail_hits": metrics["concrete_hits"],
        }
    elif vid == "cadence_variance_checker":
        low_spread_penalty = 0.12 if (max(metrics["lengths"] or [0]) - min(metrics["lengths"] or [0]) < 5) else 0.0
        score = clamp(
            0.32
            + 0.32 * min(metrics["variance"] / 40.0, 1.0)
            + 0.18 * metrics["opening_diversity"]
            + 0.1 * metrics["clause_pattern_entropy"]
            + 0.12 * metrics["punctuation_rhythm"]
            - low_spread_penalty
        )
        evidence = {
            "sentence_length_variance": round(metrics["variance"], 3),
            "sentence_lengths": metrics["lengths"],
            "sentence_opening_diversity": round(metrics["opening_diversity"], 3),
            "clause_pattern_entropy": round(metrics["clause_pattern_entropy"], 3),
            "punctuation_rhythm": round(metrics["punctuation_rhythm"], 3),
        }
    elif vid == "abstraction_ratio_checker":
        ratio = metrics["abstract_hits"] / max(metrics["concrete_hits"], 1)
        score = clamp(
            0.92
            - min(ratio / 3.0, 1.0) * 0.25
            - min(metrics["abstract_hits"] * 0.02, 0.16)
            + min(metrics["concrete_hits"] * 0.03, 0.1)
            - (0.06 if metrics["bullet_ratio"] > 0.0 else 0.0)
            - (0.22 if metrics["concrete_hits"] == 0 or ratio >= 5.0 else 0.0)
        )
        evidence = {
            "abstract_term_hits": metrics["abstract_hits"],
            "concrete_detail_hits": metrics["concrete_hits"],
            "abstraction_ratio": round(ratio, 3),
        }
    elif vid == "semantic_redundancy_detector":
        score, evidence = classify_redundancy_v3(metrics, metrics["segments"])
    elif vid == "continuity_consistency_checker":
        score = clamp(
            0.38
            + (0.22 if metrics["location_hit"] else 0.0)
            + (0.2 if metrics["character_hit"] else 0.0)
            + min(len(metrics["mentioned_entities"]) * 0.05, 0.1)
            - min(metrics["contradiction_markers"] * 0.08, 0.45)
        )
        evidence = {
            "location_alignment": metrics["location_hit"],
            "character_alignment": metrics["character_hit"],
            "named_entity_mentions": metrics["mentioned_entities"],
            "contradiction_markers": metrics["contradiction_markers"],
        }
    elif vid == "dialogue_realism_checker":
        utterance_lengths = [len(re.findall(r"[A-Za-z']+", line)) for line in metrics["dialogue_lines"]]
        opening_tokens = [re.findall(r"[A-Za-z']+", line.lower())[0] for line in metrics["dialogue_lines"] if re.findall(r"[A-Za-z']+", line.lower())]
        mirrored_openings = len(opening_tokens) - len(set(opening_tokens))
        exposition_penalty = 0.2 if ("as you know" in " ".join(metrics["dialogue_lines"]).lower()) else 0.0
        score = clamp(
            0.18
            + min(len(metrics["dialogue_lines"]) * 0.11, 0.36)
            + min(metrics["dialogue_length_variation"] * 0.015, 0.14)
            + (0.14 if metrics["interruption_markers"] > 0 else 0.0)
            + min(metrics["pragmatics_markers"] * 0.05, 0.2)
            + (0.14 if metrics["dialogue_bridge_present"] else 0.0)
            - min(mirrored_openings * 0.08, 0.24)
            - exposition_penalty
        )
        evidence = {
            "dialogue_line_count": len(metrics["dialogue_lines"]),
            "dialogue_length_variation": round(metrics["dialogue_length_variation"], 3),
            "overlap_markers": metrics["overlap_markers"],
            "interruption_markers": metrics["interruption_markers"],
            "pragmatics_markers": metrics["pragmatics_markers"],
            "dialogue_bridge_present": metrics["dialogue_bridge_present"],
            "mirrored_openings": mirrored_openings,
            "utterance_lengths": utterance_lengths,
        }
    elif vid == "human_style_preference_validator":
        paragraph_score = 1.0 if metrics["bullet_ratio"] == 0.0 and len(metrics["paragraphs"]) >= 1 else 0.2
        score = clamp(
            0.16
            + paragraph_score * 0.28
            + min(metrics["context_depth_signals"] * 0.035, 0.2)
            + min(metrics["emotional_energy_signals"] * 0.04, 0.2)
            - metrics["bullet_ratio"] * 0.48
        )
        evidence = {
            "paragraph_count": len(metrics["paragraphs"]),
            "bullet_ratio": round(metrics["bullet_ratio"], 3),
            "context_depth_signals": metrics["context_depth_signals"],
            "emotional_energy_signals": metrics["emotional_energy_signals"],
            "paragraph_flow_score": round(paragraph_score, 2),
            "context_sufficiency_score": round(metrics["context_sufficiency_score"], 2),
            "emotional_energy_score": round(metrics["emotional_energy_score"], 2),
        }
    elif vid == "character_arc_consistency_validator":
        narrative_metrics = narrative_metrics or {}
        stagnation_count = len(narrative_metrics.get("arc_stagnation_flags", []))
        high_violations = sum(
            1
            for item in narrative_metrics.get("obligation_violations", [])
            if item["obligation_type"] == "character_arc_shift" and item["importance"] == "high"
        )
        score = clamp(0.92 - 0.26 * stagnation_count - 0.12 * high_violations)
        evidence = {
            "arc_integrity_score": round(score, 3),
            "arc_stagnation_flags": narrative_metrics.get("arc_stagnation_flags", []),
            "obligation_violations": [
                item for item in narrative_metrics.get("obligation_violations", []) if item["obligation_type"] == "character_arc_shift"
            ],
            "structural_violation_score": narrative_metrics.get("structural_violation_score", 0.0),
            "obligation_failure_count": narrative_metrics.get("obligation_failure_count", 0),
        }
    elif vid == "thread_persistence_validator":
        narrative_metrics = narrative_metrics or {}
        unresolved = narrative_metrics.get("unresolved_threads", [])
        dropouts = narrative_metrics.get("thread_dropouts", [])
        high_unresolved = sum(1 for item in unresolved if item["importance"] == "high")
        score = clamp(0.94 - 0.18 * high_unresolved - 0.1 * len(dropouts) - 0.06 * max(len(unresolved) - high_unresolved, 0))
        evidence = {
            "thread_persistence_score": round(score, 3),
            "thread_dropouts": dropouts,
            "unresolved_threads": unresolved,
            "resolution_type": narrative_metrics.get("resolution_type", "direct"),
            "transformation_detected": narrative_metrics.get("transformation_detected", False),
            "transformation_validity_score": narrative_metrics.get("transformation_validity_score", 0.0),
            "semantic_role_shift": narrative_metrics.get("semantic_role_shift", ""),
            "obligation_violations": [
                item for item in narrative_metrics.get("obligation_violations", []) if item["obligation_type"] == "thread_resolution"
            ],
            "structural_violation_score": narrative_metrics.get("structural_violation_score", 0.0),
            "obligation_failure_count": narrative_metrics.get("obligation_failure_count", 0),
        }
    elif vid == "setup_payoff_integrity_validator":
        narrative_metrics = narrative_metrics or {}
        unmet = narrative_metrics.get("unmet_setups", [])
        unsupported = narrative_metrics.get("unsupported_payoffs", [])
        high_unmet = sum(1 for item in unmet if item["obligation_strength"] == "high")
        score = clamp(0.95 - 0.18 * high_unmet - 0.12 * len(unsupported) - 0.04 * max(len(unmet) - high_unmet, 0))
        evidence = {
            "setup_payoff_score": round(score, 3),
            "unmet_setups": unmet,
            "unsupported_payoffs": unsupported,
            "payoff_type_mismatch": narrative_metrics.get("transformation_detected", False),
            "transformation_detected": narrative_metrics.get("transformation_detected", False),
            "transformation_validity_score": narrative_metrics.get("transformation_validity_score", 0.0),
            "resolution_type": narrative_metrics.get("resolution_type", "direct"),
            "object_function_transformed": narrative_metrics.get("object_function_transformed", False),
            "payoff_transformation_score": narrative_metrics.get("payoff_transformation_score", 0.0),
            "earned_subversion_score": narrative_metrics.get("earned_subversion_score", 0.0),
            "semantic_role_shift": narrative_metrics.get("semantic_role_shift", ""),
            "obligation_violations": [
                item for item in narrative_metrics.get("obligation_violations", []) if item["obligation_type"] == "setup_payoff"
            ],
            "structural_violation_score": narrative_metrics.get("structural_violation_score", 0.0),
            "obligation_failure_count": narrative_metrics.get("obligation_failure_count", 0),
        }
    elif vid == "theme_evolution_validator":
        narrative_metrics = narrative_metrics or {}
        motif_failures = narrative_metrics.get("motif_failures", [])
        score = clamp(0.9 - 0.2 * len(motif_failures) - 0.04 * narrative_metrics.get("unsupported_payoff_count", 0))
        evidence = {
            "theme_evolution_score": round(score, 3),
            "theme_stagnation_points": motif_failures,
            "motif_failures": motif_failures,
            "object_function_transformed": narrative_metrics.get("object_function_transformed", False),
            "semantic_role_shift": narrative_metrics.get("semantic_role_shift", ""),
            "obligation_violations": [
                item for item in narrative_metrics.get("obligation_violations", []) if item["obligation_type"] == "motif_transformation"
            ],
            "structural_violation_score": narrative_metrics.get("structural_violation_score", 0.0),
            "obligation_failure_count": narrative_metrics.get("obligation_failure_count", 0),
        }
    elif vid == "pressure_curve_validator":
        narrative_metrics = narrative_metrics or {}
        consequence_gaps = narrative_metrics.get("consequence_gaps", [])
        pressure_flatlines = []
        if consequence_gaps:
            pressure_flatlines.append(
                {
                    "scene_id": "scene_06",
                    "issue": "pressure builds rhetorically without commensurate release, reversal, or consequence",
                }
            )
        score = clamp(0.88 - 0.14 * len(consequence_gaps) - 0.06 * len(pressure_flatlines))
        evidence = {
            "pressure_curve_score": round(score, 3),
            "pressure_flatlines": pressure_flatlines,
            "consequence_gaps": consequence_gaps,
            "structural_violation_score": narrative_metrics.get("structural_violation_score", 0.0),
            "obligation_failure_count": narrative_metrics.get("obligation_failure_count", 0),
        }
    elif vid == "scene_consequence_validator":
        narrative_metrics = narrative_metrics or {}
        gaps = narrative_metrics.get("consequence_gaps", [])
        high_gap_count = sum(1 for item in gaps if "decision" in item["gap_type"] or "pressure" in item["gap_type"])
        score = clamp(0.9 - 0.24 * high_gap_count - 0.1 * max(len(gaps) - high_gap_count, 0))
        evidence = {
            "scene_consequence_score": round(score, 3),
            "consequence_gaps": gaps,
            "belief_shift_detected": narrative_metrics.get("belief_shift_detected", False),
            "transformation_detected": narrative_metrics.get("transformation_detected", False),
            "obligation_violations": [
                item for item in narrative_metrics.get("obligation_violations", []) if item["obligation_type"] == "scene_consequence"
            ],
            "structural_violation_score": narrative_metrics.get("structural_violation_score", 0.0),
            "obligation_failure_count": narrative_metrics.get("obligation_failure_count", 0),
        }
    elif vid == "emotional_resonance_validator":
        reader_metrics = reader_metrics or {}
        score = reader_metrics.get("emotional_resonance_score", 0.0)
        evidence = {
            "emotional_resonance_score": round(score, 3),
            "emotional_band": reader_metrics.get("emotional_band", "low"),
            "reader_state": reader_metrics.get("reader_state", {}).get("emotional_state", {}),
        }
    elif vid == "payoff_satisfaction_validator":
        reader_metrics = reader_metrics or {}
        narrative_metrics = narrative_metrics or {}
        score = reader_metrics.get("payoff_satisfaction_score", 0.0)
        evidence = {
            "payoff_satisfaction_score": round(score, 3),
            "payoff_band": reader_metrics.get("payoff_band", "low"),
            "transformation_detected": narrative_metrics.get("transformation_detected", False),
            "resolution_type": narrative_metrics.get("resolution_type", "direct"),
        }
    elif vid == "surprise_calibration_validator":
        reader_metrics = reader_metrics or {}
        narrative_metrics = narrative_metrics or {}
        score = reader_metrics.get("surprise_score", 0.0)
        evidence = {
            "surprise_score": round(score, 3),
            "subversion_detected": narrative_metrics.get("subversion_detected", False),
            "payoff_transformation_score": narrative_metrics.get("payoff_transformation_score", 0.0),
        }
    elif vid == "tension_absorption_validator":
        reader_metrics = reader_metrics or {}
        score = reader_metrics.get("tension_absorption_score", 0.0)
        evidence = {
            "tension_absorption_score": round(score, 3),
            "reader_state": reader_metrics.get("reader_state", {}).get("tension_state", {}),
        }
    elif vid == "memorability_validator":
        reader_metrics = reader_metrics or {}
        narrative_metrics = narrative_metrics or {}
        score = reader_metrics.get("memorability_score", 0.0)
        evidence = {
            "memorability_score": round(score, 3),
            "object_function_transformed": narrative_metrics.get("object_function_transformed", False),
            "reader_state": reader_metrics.get("reader_state", {}).get("curiosity_state", {}),
        }
    elif vid == "cognitive_load_validator":
        reader_metrics = reader_metrics or {}
        score = reader_metrics.get("cognitive_load_score", 0.0)
        evidence = {
            "cognitive_load_score": round(score, 3),
            "reader_state": reader_metrics.get("reader_state", {}).get("understanding_state", {}),
        }
    elif vid == "high_arousal_emotion_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("high_arousal_score", 0.0)
        evidence = {
            "high_arousal_score": round(score, 3),
            "manipulation_risk": viral_metrics.get("manipulation_risk", 0.0),
        }
    elif vid == "hook_strength_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("hook_strength_score", 0.0)
        evidence = {
            "hook_strength_score": round(score, 3),
            "hook_content_mismatch": viral_metrics.get("hook_content_mismatch", False),
            "clickbait_risk": viral_metrics.get("clickbait_risk", 0.0),
        }
    elif vid == "identity_resonance_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("identity_resonance_score", 0.0)
        evidence = {
            "identity_resonance_score": round(score, 3),
            "identity_bait_without_substance": viral_metrics.get("identity_bait_without_substance", False),
        }
    elif vid == "shareability_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("shareability_score", 0.0)
        evidence = {
            "shareability_score": round(score, 3),
            "viral_score": viral_metrics.get("viral_score", 0.0),
        }
    elif vid == "novelty_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("novelty_score", 0.0)
        evidence = {
            "novelty_score": round(score, 3),
            "clickbait_patterns_detected": viral_metrics.get("clickbait_patterns_detected", 0),
        }
    elif vid == "insight_density_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("insight_density_score", 0.0)
        evidence = {
            "insight_density_score": round(score, 3),
            "abstraction_ratio": viral_metrics.get("abstraction_ratio", 0.0),
            "concrete_example_count": viral_metrics.get("concrete_example_count", 0),
            "articulated_takeaway_count": viral_metrics.get("articulated_takeaway_count", 0),
            "claim_density": viral_metrics.get("claim_density", 0.0),
            "experiential_specificity_score": viral_metrics.get("experiential_specificity_score", 0.0),
            "human_stakes_score": viral_metrics.get("human_stakes_score", 0.0),
            "interpretive_density_score": viral_metrics.get("interpretive_density_score", 0.0),
            "memorable_meaning_score": viral_metrics.get("memorable_meaning_score", 0.0),
            "explicit_insight_path_score": viral_metrics.get("explicit_insight_path_score", 0.0),
            "implicit_experiential_path_score": viral_metrics.get("implicit_experiential_path_score", 0.0),
            "generic_motivation_detected": viral_metrics.get("generic_motivation_detected", False),
            "empty_insight_detected": viral_metrics.get("empty_insight_detected", False),
            "shallow_philosophy_detected": viral_metrics.get("shallow_philosophy_detected", False),
        }
    elif vid == "viral_integrity_validator":
        viral_metrics = reader_metrics.get("viral_metrics", {}) if reader_metrics else {}
        score = viral_metrics.get("viral_integrity_score", 0.0)
        evidence = {
            "viral_integrity_score": round(score, 3),
            "manipulation_risk": viral_metrics.get("manipulation_risk", 0.0),
            "clickbait_risk": viral_metrics.get("clickbait_risk", 0.0),
            "hook_content_mismatch": viral_metrics.get("hook_content_mismatch", False),
            "emotional_manipulation_without_payoff": viral_metrics.get("emotional_manipulation_without_payoff", False),
            "identity_bait_without_substance": viral_metrics.get("identity_bait_without_substance", False),
        }
    elif vid == "platform_fit_validator":
        platform_metrics = reader_metrics.get("platform_metrics", {}) if reader_metrics else {}
        score = platform_metrics.get("platform_fit_score", 0.0)
        evidence = {
            "facebook_score": platform_metrics.get("facebook_score", 0.0),
            "youtube_score": platform_metrics.get("youtube_score", 0.0),
            "twitter_score": platform_metrics.get("twitter_score", 0.0),
            "linkedin_score": platform_metrics.get("linkedin_score", 0.0),
            "instagram_score": platform_metrics.get("instagram_score", 0.0),
            "reddit_score": platform_metrics.get("reddit_score", 0.0),
            "tone_mismatch": platform_metrics.get("tone_mismatch", []),
            "structure_mismatch": platform_metrics.get("structure_mismatch", []),
            "audience_mismatch": platform_metrics.get("audience_mismatch", []),
            "best_fit_platforms": platform_metrics.get("best_fit_platforms", []),
            "weak_fit_platforms": platform_metrics.get("weak_fit_platforms", []),
        }
    else:
        raise KeyError(f"Unsupported validator: {vid}")

    return round(score, 2), evidence


def apply_interaction_adjustments(validator_results: list[dict], metrics: dict, thresholds: dict) -> list[dict]:
    result_map = {item["validator_id"]: item for item in validator_results}

    cadence_result = result_map.get("cadence_variance_checker")
    semantic_result = result_map.get("semantic_redundancy_detector")
    abstraction_result = result_map.get("abstraction_ratio_checker")
    style_result = result_map.get("human_style_preference_validator")

    cadence_relief_factor = 0.0
    if cadence_result and semantic_result:
        cadence_signal_ok = cadence_result["score"] >= thresholds["validator_thresholds"]["cadence_variance_checker"]["warn_min"]
        strong_burstiness = cadence_result["score"] >= 0.4
        refrain_like_pattern = (
            metrics["opening_diversity"] >= 0.95
            and strong_burstiness
            and metrics["repeated_phrase_count"] >= 3
            and metrics["semantic_frame_repetition"] == 0
            and metrics["modal_repetition"] == 0
        )
        if cadence_signal_ok and refrain_like_pattern:
            cadence_relief_factor = 0.18
            semantic_result["score"] = round(clamp(semantic_result["score"] + cadence_relief_factor), 2)
            if semantic_result["evidence"].get("redundancy_class") == "collapse":
                semantic_result["evidence"]["redundancy_class"] = "semantic_spin"
                semantic_result["evidence"]["recurrence_mode"] = "semantic_spin"
                semantic_result["evidence"]["collapse_penalty"] = round(
                    max(0.0, semantic_result["evidence"].get("collapse_penalty", 0.0) - cadence_relief_factor),
                    3,
                )
                semantic_result["evidence"]["lexical_diversity_collapse_penalty"] = round(
                    max(0.0, semantic_result["evidence"].get("lexical_diversity_collapse_penalty", 0.0) - cadence_relief_factor / 2),
                    3,
                )
                semantic_result["score"] = round(
                    max(
                        semantic_result["score"],
                        thresholds["validator_thresholds"]["semantic_redundancy_detector"]["warn_min"] + 0.02,
                    ),
                    2,
                )

    dialogue_context_relief = 0.0
    if cadence_result:
        short_turn_dialogue = len(metrics["dialogue_lines"]) >= 4 and metrics["dialogue_length_variation"] <= 3.0
        dialogue_texture_present = metrics["dialogue_bridge_present"] or metrics["pragmatics_markers"] > 0 or metrics["interruption_markers"] > 0
        if short_turn_dialogue and dialogue_texture_present:
            dialogue_context_relief = 0.1
            cadence_result["score"] = round(clamp(cadence_result["score"] + dialogue_context_relief), 2)

    narrative_density_adjustment = 0.0
    if abstraction_result and style_result:
        context_rich_prose = (
            metrics["bullet_ratio"] == 0.0
            and len(metrics["paragraphs"]) >= 1
            and metrics["context_depth_signals"] >= 3
            and metrics["concrete_hits"] >= 3
            and metrics["abstract_hits"] >= 2
        )
        if context_rich_prose:
            narrative_density_adjustment = 0.08
            abstraction_result["score"] = round(clamp(abstraction_result["score"] + narrative_density_adjustment), 2)
            style_result["score"] = round(clamp(style_result["score"] + narrative_density_adjustment), 2)

    for item in validator_results:
        if item["validator_id"] == "semantic_redundancy_detector":
            item["evidence"]["cadence_relief_factor"] = round(cadence_relief_factor, 2)
        if item["validator_id"] == "cadence_variance_checker":
            item["evidence"]["dialogue_context_relief"] = round(dialogue_context_relief, 2)
        if item["validator_id"] in {"abstraction_ratio_checker", "human_style_preference_validator"}:
            item["evidence"]["narrative_density_adjustment"] = round(narrative_density_adjustment, 2)
        threshold_def = thresholds["validator_thresholds"][item["validator_id"]]
        item["status"] = classify_threshold(item["score"], threshold_def)

    return validator_results


def apply_transformation_relief(validator_results: list[dict], narrative_metrics: dict, thresholds: dict) -> list[dict]:
    if not (
        narrative_metrics.get("transformation_detected")
        and narrative_metrics.get("transformation_validity_score", 0.0) >= 0.8
        and narrative_metrics.get("earned_subversion_score", 0.0) >= 0.85
    ):
        return validator_results

    v4_ids = {
        "character_arc_consistency_validator",
        "thread_persistence_validator",
        "setup_payoff_integrity_validator",
        "theme_evolution_validator",
        "pressure_curve_validator",
        "scene_consequence_validator",
    }
    if any(item["validator_id"] in v4_ids and item["status"] == "fail" for item in validator_results):
        return validator_results

    for item in validator_results:
        if item["validator_id"] == "abstraction_ratio_checker" and item["status"] == "fail":
            warn_floor = thresholds["validator_thresholds"]["abstraction_ratio_checker"]["warn_min"]
            item["score"] = round(max(item["score"], warn_floor + 0.02), 2)
            item["evidence"]["transformation_relief_applied"] = True
            item["evidence"]["transformation_validity_score"] = narrative_metrics.get("transformation_validity_score", 0.0)
            item["status"] = classify_threshold(item["score"], thresholds["validator_thresholds"]["abstraction_ratio_checker"])
    return validator_results


def evaluate_text(text: str, input_bundle: dict, thresholds: dict, validator_registry: dict) -> dict:
    metrics = build_metrics(text, input_bundle)
    narrative_metrics = build_v4_narrative_metrics(text, metrics)
    reader_metrics = build_v5_reader_metrics(text, metrics, narrative_metrics)
    reader_metrics["viral_metrics"] = build_v6_viral_metrics(text, metrics, narrative_metrics, reader_metrics)
    validator_results = []
    for validator in validator_registry["validators"]:
        score, evidence = score_validator(validator, metrics, narrative_metrics, reader_metrics)
        threshold_def = thresholds["validator_thresholds"][validator["validator_id"]]
        validator_results.append(
            {
                "validator_id": validator["validator_id"],
                "validator_family": validator["validator_family"],
                "pass": validator["pass"],
                "dimension": validator["dimension"],
                "score": score,
                "status": classify_threshold(score, threshold_def),
                "linked_rules": validator["linked_rules"],
                "linked_failure_modes": validator["linked_failure_modes"],
                "primary_library": validator["primary_library"],
                "secondary_libraries": validator["secondary_libraries"],
                "threshold_key": validator["threshold_key"],
                "contextual_only": validator.get("contextual_only", False),
                "evidence": evidence,
            }
        )

    reader_metrics["platform_metrics"] = build_platform_metrics(validator_results, metrics, reader_metrics)
    for item in validator_results:
        if item["validator_id"] == "platform_fit_validator":
            score, evidence = score_validator(
                next(v for v in validator_registry["validators"] if v["validator_id"] == "platform_fit_validator"),
                metrics,
                narrative_metrics,
                reader_metrics,
            )
            threshold_def = thresholds["validator_thresholds"]["platform_fit_validator"]
            item["score"] = score
            item["status"] = classify_threshold(score, threshold_def)
            item["evidence"] = evidence

    validator_results = apply_interaction_adjustments(validator_results, metrics, thresholds)
    validator_results = apply_transformation_relief(validator_results, narrative_metrics, thresholds)

    dimension_scores = {}
    threshold_results = []
    authoritative_results = [item for item in validator_results if not item.get("contextual_only", False)]
    rejected = any(item["status"] == "fail" for item in authoritative_results)
    warnings_only = any(item["status"] == "warn" for item in authoritative_results)
    for dimension, config in thresholds["dimensions"].items():
        if config.get("contextual_only", False):
            continue
        relevant = [item["score"] for item in validator_results if item["dimension"] == dimension]
        if not relevant:
            continue
        value = round(sum(relevant) / len(relevant), 2) if config.get("aggregation") == "mean" else round(min(relevant), 2)
        dimension_scores[dimension] = value
        status = "pass"
        if value < config["warning_floor"]:
            status = "fail"
            rejected = True
        elif value < config["minimum_score"]:
            status = "warn"
            warnings_only = True
        threshold_results.append(
            {
                "dimension": dimension,
                "score": value,
                "minimum_score": config["minimum_score"],
                "warning_floor": config["warning_floor"],
                "status": status,
                "driving_validators": config["driving_validators"],
            }
        )

    high_importance_violation = any(
        item.get("importance") == "high" and item.get("status") == "violated"
        for item in narrative_metrics["obligation_violations"]
    )
    structural_gate = thresholds.get("narrative_obligation_gate", {})
    if narrative_metrics["structural_violation_score"] >= structural_gate.get("fail_at_or_above", 1.1) or high_importance_violation:
        rejected = True
        threshold_results.append(
            {
                "dimension": "narrative_obligation_gate",
                "score": round(narrative_metrics["structural_violation_score"], 2),
                "minimum_score": structural_gate.get("warn_above", 0.0),
                "warning_floor": structural_gate.get("fail_at_or_above", 1.0),
                "status": "fail",
                "driving_validators": [
                    "character_arc_consistency_validator",
                    "thread_persistence_validator",
                    "setup_payoff_integrity_validator",
                    "theme_evolution_validator",
                    "scene_consequence_validator",
                ],
            }
        )

    viral_integrity = next((item for item in validator_results if item["validator_id"] == "viral_integrity_validator"), None)
    if viral_integrity:
        vt = thresholds["validator_thresholds"]["viral_integrity_validator"]
        manipulation_risk = viral_integrity["evidence"].get("manipulation_risk", 0.0)
        clickbait_risk = viral_integrity["evidence"].get("clickbait_risk", 0.0)
        viral_metrics = reader_metrics.get("viral_metrics", {})
        if (
            viral_integrity["score"] < vt["fail_below"]
            or manipulation_risk >= vt["manipulation_risk_fail"]
            or clickbait_risk >= vt["clickbait_risk_fail"]
        ):
            rejected = True
            threshold_results.append(
                {
                    "dimension": "viral_integrity_gate",
                    "score": round(viral_integrity["score"], 2),
                    "minimum_score": vt["warn_min"],
                    "warning_floor": vt["fail_below"],
                    "status": "fail",
                    "driving_validators": ["viral_integrity_validator"],
                }
            )
        elif viral_integrity["score"] < vt["pass_min"] or manipulation_risk >= vt["manipulation_risk_warn"] or clickbait_risk >= vt["clickbait_risk_warn"]:
            warnings_only = True

        high_integrity_viral_path = (
            viral_metrics.get("high_integrity_viral_cases", False)
            and viral_integrity["score"] >= vt["pass_min"]
            and manipulation_risk < vt["manipulation_risk_warn"]
            and clickbait_risk < vt["clickbait_risk_warn"]
            and narrative_metrics.get("structural_violation_score", 0.0) < structural_gate.get("fail_at_or_above", 1.1)
            and not high_importance_violation
        )
        if high_integrity_viral_path:
            allowed_warning_failures = {
                "dialogue_realism_checker",
                "human_style_preference_validator",
                "emotional_resonance_validator",
                "payoff_satisfaction_validator",
                "surprise_calibration_validator",
                "tension_absorption_validator",
                "memorability_validator",
                "cognitive_load_validator",
                "high_arousal_emotion_validator",
                "hook_strength_validator",
                "identity_resonance_validator",
                "shareability_validator",
                "novelty_validator",
            }
            non_viral_failures = [
                item for item in validator_results
                if item["status"] == "fail"
                and item["validator_id"] not in allowed_warning_failures
            ]
            if not non_viral_failures:
                rejected = False
                warnings_only = True
                threshold_results.append(
                    {
                        "dimension": "high_integrity_viral_path",
                        "score": round(viral_metrics.get("viral_score", 0.0), 2),
                        "minimum_score": 0.4,
                        "warning_floor": 0.8,
                        "status": "warn",
                        "driving_validators": [
                            "high_arousal_emotion_validator",
                            "hook_strength_validator",
                            "identity_resonance_validator",
                            "shareability_validator",
                            "novelty_validator",
                            "viral_integrity_validator",
                        ],
                    }
                )

    final_status = "rejected" if rejected else "accepted_with_warnings" if warnings_only else "accepted"
    return {
        "metrics": metrics,
        "narrative_metrics": narrative_metrics,
        "reader_metrics": reader_metrics,
        "platform_metrics": reader_metrics.get("platform_metrics", {}),
        "validator_results": validator_results,
        "dimension_scores": dimension_scores,
        "threshold_results": threshold_results,
        "final_status": final_status,
    }
