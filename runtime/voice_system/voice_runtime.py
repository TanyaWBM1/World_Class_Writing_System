from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VOICE_PROFILE_PATH = ROOT / "runtime" / "voice_system" / "voice_profile_tanya_lawson_v1.json"
VOCABULARY_PROFILE_PATH = ROOT / "runtime" / "voice_system" / "vocabulary_profile_tanya_lawson.json"
LIVE_WORD_BLACKLIST_PATH = ROOT / "runtime" / "voice_system" / "live_word_blacklist.json"
REWRITE_MAP_PATH = ROOT / "runtime" / "voice_system" / "rewrite_map_tanya_lawson.json"
LEXICAL_EDIT_LOG_PATH = ROOT / "runtime" / "voice_system" / "lexical_edit_log.json"
CADENCE_RULES_PATH = ROOT / "runtime" / "voice_system" / "tanya_cadence_rules.json"
THOUGHT_VISIBILITY_RULES_PATH = ROOT / "runtime" / "voice_system" / "thought_visibility_rules.json"


def load_voice_profile() -> dict:
    return json.loads(VOICE_PROFILE_PATH.read_text(encoding="utf-8"))


def load_vocabulary_profile() -> dict:
    return json.loads(VOCABULARY_PROFILE_PATH.read_text(encoding="utf-8"))


def load_live_word_blacklist() -> dict:
    return json.loads(LIVE_WORD_BLACKLIST_PATH.read_text(encoding="utf-8"))


def load_rewrite_map() -> dict:
    return json.loads(REWRITE_MAP_PATH.read_text(encoding="utf-8"))


def load_lexical_edit_log() -> dict:
    return json.loads(LEXICAL_EDIT_LOG_PATH.read_text(encoding="utf-8"))


def load_cadence_rules() -> dict:
    return json.loads(CADENCE_RULES_PATH.read_text(encoding="utf-8"))


def load_thought_visibility_rules() -> dict:
    return json.loads(THOUGHT_VISIBILITY_RULES_PATH.read_text(encoding="utf-8"))


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def sentence_segments(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def paragraph_segments(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def sentence_lengths(text: str) -> list[int]:
    lengths = []
    for segment in sentence_segments(text):
        tokens = re.findall(r"[A-Za-z']+", segment)
        if tokens:
            lengths.append(len(tokens))
    return lengths


def analyze_cadence(text: str) -> dict:
    cadence_contract = load_cadence_rules()
    rules = cadence_contract["rules"]
    roughness_rules = cadence_contract.get("roughness_rules", {})
    paragraphs = paragraph_segments(text)
    sentences = sentence_segments(text)
    lengths = sentence_lengths(text)
    short_sentences = sum(1 for value in lengths if value <= 6)
    short_ratio = short_sentences / max(1, len(lengths))
    avg_sentences_per_paragraph = len(sentences) / max(1, len(paragraphs))
    one_sentence_paragraphs = sum(1 for paragraph in paragraphs if len(sentence_segments(paragraph)) <= 1)
    stacked_short_lines = sum(
        1 for line in text.splitlines() if line.strip() and len(re.findall(r"[A-Za-z']+", line)) <= 10
    )
    punchline_spacing = max(0, stacked_short_lines - 1) if len(paragraphs) > 1 else 0
    underdeveloped_ideas = sum(1 for paragraph in paragraphs if len(sentence_segments(paragraph)) < 3)
    mean_len = sum(lengths) / len(lengths) if lengths else 0.0
    variance = sum((value - mean_len) ** 2 for value in lengths) / len(lengths) if lengths else 0.0
    excessive_line_breaks = text.count("\n") > max(5, len(paragraphs) * 3)
    uniform_length_flag = bool(lengths) and variance < 8.0
    overly_clean_transitions = len(re.findall(r"\b(first|second|finally|therefore|moreover|in conclusion)\b", text.lower())) >= 2
    reflection_pause_present = bool(re.search(r"\b(maybe|still|but|and yet|I keep|I wonder)\b", text, flags=re.IGNORECASE))
    tension_presence_score = clamp(
        0.25
        + 0.32 * float(reflection_pause_present)
        + 0.22 * float(any(value >= 16 for value in lengths))
        + 0.21 * float(len(paragraphs) >= 2)
        - 0.24 * float(overly_clean_transitions)
    )
    underdeveloped_ideas_flag = (
        avg_sentences_per_paragraph < rules["min_avg_sentences_per_paragraph"]
        or underdeveloped_ideas > max(1, len(paragraphs) // 2)
    )
    compression_flags = []
    if short_ratio > rules["max_short_sentence_ratio"]:
        compression_flags.append("high_short_sentence_ratio")
    if stacked_short_lines >= 3:
        compression_flags.append("stacked_short_lines")
    if punchline_spacing >= 2:
        compression_flags.append("punchline_spacing")
    if underdeveloped_ideas_flag:
        compression_flags.append("underdeveloped_ideas")
    if uniform_length_flag:
        compression_flags.append("uniform_sentence_length")
    if excessive_line_breaks:
        compression_flags.append("excessive_line_breaks")
    if overly_clean_transitions:
        compression_flags.append("overly_clean_transitions")
    if not reflection_pause_present:
        compression_flags.append("missing_reflection_pause")
    over_polish_flags = []
    if overly_clean_transitions:
        over_polish_flags.append("overly_clean_transitions")
    if uniform_length_flag:
        over_polish_flags.append("uniform_sentence_flow")
    if not reflection_pause_present:
        over_polish_flags.append("low_tension_presence")
    cadence_naturalness_score = clamp(
        0.3
        + 0.22 * min(avg_sentences_per_paragraph / max(rules["min_avg_sentences_per_paragraph"], 1), 1.0)
        + 0.2 * min(variance / 28.0, 1.0)
        + 0.18 * (1.0 - min(short_ratio / max(rules["max_short_sentence_ratio"], 0.01), 1.0))
        + 0.1 * float(len(paragraphs) >= 2)
        - 0.18 * min(punchline_spacing / 3.0, 1.0)
        - 0.12 * float(excessive_line_breaks)
    )
    development_depth_score = clamp(
        0.28
        + 0.34 * min(avg_sentences_per_paragraph / max(rules["min_avg_sentences_per_paragraph"], 1), 1.0)
        + 0.2 * float(any(value >= 18 for value in lengths))
        + 0.18 * float(len(paragraphs) >= 2)
        - 0.28 * min(underdeveloped_ideas / max(1, len(paragraphs)), 1.0)
    )
    compression_score = clamp(
        0.26 * min(short_ratio / max(rules["max_short_sentence_ratio"], 0.01), 1.0)
        + 0.22 * min(one_sentence_paragraphs / max(1, len(paragraphs)), 1.0)
        + 0.18 * min(punchline_spacing / 3.0, 1.0)
        + 0.18 * float(uniform_length_flag)
        + 0.16 * float(excessive_line_breaks)
    )
    roughness_score = clamp(
        0.26
        + 0.28 * float(not overly_clean_transitions)
        + 0.24 * tension_presence_score
        + 0.12 * float(not uniform_length_flag)
        + 0.1 * float(roughness_rules.get("prevent_over_smoothing", False))
        - 0.18 * min(punchline_spacing / 3.0, 1.0)
    )
    return {
        "rules": rules,
        "roughness_rules": roughness_rules,
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "avg_sentences_per_paragraph": round(avg_sentences_per_paragraph, 3),
        "short_sentence_ratio": round(short_ratio, 3),
        "stacked_short_lines": stacked_short_lines,
        "punchline_spacing_count": punchline_spacing,
        "underdeveloped_idea_count": underdeveloped_ideas,
        "uniform_length_flag": uniform_length_flag,
        "underdeveloped_ideas_flag": underdeveloped_ideas_flag,
        "excessive_line_breaks": excessive_line_breaks,
        "overly_clean_transitions": overly_clean_transitions,
        "reflection_pause_present": reflection_pause_present,
        "cadence_naturalness_score": round(cadence_naturalness_score, 3),
        "development_depth_score": round(development_depth_score, 3),
        "compression_score": round(compression_score, 3),
        "compression_flags": compression_flags,
        "roughness_score": round(roughness_score, 3),
        "over_polish_flags": over_polish_flags,
        "tension_presence_score": round(tension_presence_score, 3),
    }


def merge_short_sentences(text: str) -> str:
    paragraphs = paragraph_segments(text)
    rebuilt = []
    for paragraph in paragraphs:
        segments = sentence_segments(paragraph)
        if len(segments) < 2:
            rebuilt.append(paragraph)
            continue
        merged = []
        idx = 0
        while idx < len(segments):
            current = segments[idx]
            current_len = len(re.findall(r"[A-Za-z']+", current))
            if current_len <= 6 and idx + 1 < len(segments):
                merged.append(f"{current.rstrip(',;:')} and {segments[idx + 1][0].lower()}{segments[idx + 1][1:]}")
                idx += 2
                continue
            merged.append(current)
            idx += 1
        rebuilt.append(". ".join(merged).strip() + ".")
    return "\n\n".join(rebuilt)


def expand_underdeveloped_sections(text: str) -> str:
    paragraphs = paragraph_segments(text)
    expanded = []
    for paragraph in paragraphs:
        if len(sentence_segments(paragraph)) >= 3:
            expanded.append(paragraph)
            continue
        addition = "That matters because the point usually needs one more beat of context before it can land like lived thought instead of a polished line."
        if addition.lower() in paragraph.lower():
            expanded.append(paragraph)
        else:
            expanded.append(f"{paragraph} {addition}")
    return "\n\n".join(expanded)


def inject_context_if_missing(text: str) -> str:
    cadence = analyze_cadence(text)
    if not cadence["underdeveloped_ideas_flag"]:
        return text
    context = "The fuller truth usually shows up in sequence: what happened, what it exposed, and why the person inside it could not keep calling it something else."
    return text.strip() + "\n\n" + context


def soften_overly_sharp_cadence(text: str) -> str:
    softened = re.sub(r"\n{3,}", "\n\n", text)
    softened = re.sub(r"(?m)^\s*([A-Z][^.!?]{0,35})\s*$", r"\1, and that is only part of it.", softened)
    return softened


def enforce_natural_thinking_rhythm(text: str) -> tuple[str, dict]:
    revised = merge_short_sentences(text)
    revised = expand_underdeveloped_sections(revised)
    revised = inject_context_if_missing(revised)
    revised = soften_overly_sharp_cadence(revised)
    return revised, analyze_cadence(revised)


def break_transitions_slightly(text: str) -> str:
    replacements = {
        "Therefore,": "So,",
        "Moreover,": "And still,",
        "In conclusion,": "What stayed with me was this:",
        "Finally,": "And then,"
    }
    revised = text
    for source, target in replacements.items():
        revised = revised.replace(source, target)
    return revised


def delay_conclusions(text: str) -> str:
    revised = re.sub(r"\b(The point is|The truth is)\b", "I am not at the end of it yet, but", text)
    return revised


def insert_intermediate_reflection(text: str) -> str:
    if re.search(r"\b(maybe|still|I keep|and yet)\b", text, flags=re.IGNORECASE):
        return text
    return text.strip() + "\n\nMaybe that is why I do not trust the neat version of it."


def allow_natural_repetition(text: str) -> str:
    if re.search(r"\bwhat stayed\b", text, flags=re.IGNORECASE):
        return text
    return text.replace("what matters", "what matters, what really matters", 1)


def reduce_sentence_symmetry(text: str) -> str:
    return re.sub(r"\bThat is why\b", "And that is why", text)


def preserve_roughness(text: str) -> tuple[str, dict]:
    revised = break_transitions_slightly(text)
    revised = delay_conclusions(revised)
    revised = insert_intermediate_reflection(revised)
    revised = allow_natural_repetition(revised)
    revised = reduce_sentence_symmetry(revised)
    return revised, analyze_cadence(revised)


def analyze_thought_visibility(text: str) -> dict:
    thought_contract = load_thought_visibility_rules()
    rules = thought_contract["thought_visibility"]
    roughness_rules = thought_contract.get("roughness_rules", {})
    paragraphs = paragraph_segments(text)
    lower = text.lower()
    experiential_markers = [
        "i remember", "i have seen", "i learned", "in the room", "at the table", "in the hallway",
        "kitchen", "church", "body", "hands", "quiet", "tired", "mother", "father", "family"
    ]
    summary_markers = [
        "the point is", "what this means is", "in short", "the lesson is", "the truth is",
        "that is why", "therefore", "ultimately", "in the end"
    ]
    process_markers = [
        "at first", "then", "before that", "after that", "what I noticed", "what changed",
        "because", "which meant", "and then", "still", "maybe", "but", "I kept"
    ]
    clean_transition_markers = ["first,", "second,", "finally,", "moreover,", "therefore,", "in conclusion,"]
    first_paragraph = paragraphs[0].lower() if paragraphs else lower
    experiential_hits = sum(lower.count(marker) for marker in experiential_markers)
    summary_hits = sum(lower.count(marker) for marker in summary_markers)
    process_hits = sum(lower.count(marker) for marker in process_markers)
    clean_transition_hits = sum(lower.count(marker) for marker in clean_transition_markers)
    paragraph_end_summaries = sum(
        1
        for paragraph in paragraphs
        if any(paragraph.lower().rstrip().endswith(marker) for marker in ["the truth is.", "the point is.", "in short."])
    )
    early_conclusion_flag = any(marker in first_paragraph for marker in summary_markers[:6]) and experiential_hits == 0
    missing_experiential_context = experiential_hits == 0
    over_summarization_flag = summary_hits > max(1, process_hits) and experiential_hits <= 1
    clean_transition_bias = clean_transition_hits >= 2 and process_hits <= clean_transition_hits
    tension_presence_score = clamp(
        0.24
        + 0.28 * float(any(marker in lower for marker in ["maybe", "still", "and yet", "I keep", "not fully"]))
        + 0.24 * float(experiential_hits > 0)
        + 0.24 * float(process_hits > 0)
        - 0.18 * min(paragraph_end_summaries / max(1, len(paragraphs)), 1.0)
    )
    thought_visibility_score = clamp(
        0.24
        + 0.28 * min(process_hits / 4.0, 1.0)
        + 0.24 * min(experiential_hits / 3.0, 1.0)
        + 0.14 * float(len(paragraphs) >= 2)
        + 0.1 * float(not early_conclusion_flag)
        - 0.24 * float(over_summarization_flag)
        - 0.14 * float(clean_transition_bias)
    )
    experiential_depth_score = clamp(
        0.22
        + 0.42 * min(experiential_hits / 4.0, 1.0)
        + 0.18 * float(any(token in lower for token in ["kitchen", "table", "hallway", "body", "quiet"]))
        + 0.18 * float(len(paragraphs) >= 2)
        - 0.24 * float(missing_experiential_context)
    )
    process_visibility_score = clamp(
        0.24
        + 0.38 * min(process_hits / 5.0, 1.0)
        + 0.18 * float(not early_conclusion_flag)
        + 0.12 * float(any(marker in lower for marker in ["maybe", "still", "but", "and then"]))
        + 0.08 * float(len(paragraphs) >= 2)
        - 0.26 * float(over_summarization_flag)
    )
    flags = []
    if early_conclusion_flag:
        flags.append("early_conclusion_without_buildup")
    if missing_experiential_context:
        flags.append("missing_experiential_context")
    if over_summarization_flag:
        flags.append("over_summarization")
    if clean_transition_bias:
        flags.append("clean_transitions_replacing_thought")
    if paragraph_end_summaries:
        flags.append("paragraph_end_summarization")
    if tension_presence_score < 0.55:
        flags.append("low_tension_presence")
    roughness_score = clamp(
        0.24
        + 0.28 * tension_presence_score
        + 0.2 * float(not clean_transition_bias)
        + 0.16 * float(not paragraph_end_summaries)
        + 0.12 * float(roughness_rules.get("prevent_over_smoothing", False))
    )
    return {
        "rules": rules,
        "roughness_rules": roughness_rules,
        "thought_visibility_score": round(thought_visibility_score, 3),
        "experiential_depth_score": round(experiential_depth_score, 3),
        "process_visibility_score": round(process_visibility_score, 3),
        "experience_presence_score": round(clamp(min(experiential_hits / 3.0, 1.0)), 3),
        "summarization_flags": flags,
        "early_conclusion_flag": early_conclusion_flag,
        "missing_experiential_context": missing_experiential_context,
        "over_summarization_flag": over_summarization_flag,
        "clean_transition_bias": clean_transition_bias,
        "paragraph_end_summaries": paragraph_end_summaries,
        "roughness_score": round(roughness_score, 3),
        "over_polish_flags": flags,
        "tension_presence_score": round(tension_presence_score, 3),
    }


def convert_summaries_into_sequences(text: str) -> str:
    replacements = {
        "The point is": "The point did not arrive all at once. It showed up in pieces, and the point is",
        "What this means is": "What happened first matters here, because what this means is",
        "The truth is": "The truth usually shows itself before people admit it, and the truth is",
        "In short": "If I slow that down and stay with it a minute longer,"
    }
    revised = text
    for source, target in replacements.items():
        revised = re.sub(rf"\b{re.escape(source)}\b", target, revised, flags=re.IGNORECASE)
    return revised


def expand_compressed_ideas(text: str) -> str:
    paragraphs = paragraph_segments(text)
    expanded = []
    for paragraph in paragraphs:
        if len(sentence_segments(paragraph)) >= 3:
            expanded.append(paragraph)
            continue
        expanded.append(
            f"{paragraph} I usually have to stay with it a little longer than that, because the meaning only becomes honest after the intermediate thought has had room to breathe."
        )
    return "\n\n".join(expanded)


def insert_lived_experience_context(text: str) -> str:
    analysis = analyze_thought_visibility(text)
    if not analysis["missing_experiential_context"]:
        return text
    addition = (
        "I do not come to that as a clean theory. I come to it from ordinary rooms, from the moment a table goes quiet or somebody's body tells the truth before their mouth does."
    )
    return text.strip() + "\n\n" + addition


def reconstruct_thinking_sequence(text: str) -> str:
    analysis = analyze_thought_visibility(text)
    if analysis["process_visibility_score"] >= 0.58:
        return text
    sequence = "At first it looked simpler than it was. Then one detail kept bothering me. After that, the meaning started to show itself in a way I could not smooth over."
    return text.strip() + "\n\n" + sequence


def enforce_thought_visibility(text: str) -> tuple[str, dict]:
    revised = convert_summaries_into_sequences(text)
    revised = expand_compressed_ideas(revised)
    revised = insert_lived_experience_context(revised)
    revised = reconstruct_thinking_sequence(revised)
    return revised, analyze_thought_visibility(revised)


def ensure_sentence_variation(text: str) -> str:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs:
        return text
    rebuilt_paragraphs = []
    starters = ["And", "But", "Maybe", "Still"]
    for p_index, paragraph in enumerate(paragraphs):
        sentences = sentence_segments(paragraph)
        if len(sentences) < 2:
            rebuilt_paragraphs.append(paragraph.strip())
            continue
        adjusted = []
        for s_index, sentence in enumerate(sentences):
            if s_index > 0 and s_index % 3 == 0 and not sentence.startswith(tuple(starters)):
                adjusted.append(f"{starters[(p_index + s_index) % len(starters)]} {sentence[0].lower()}{sentence[1:]}")
            else:
                adjusted.append(sentence)
        rebuilt = ". ".join(adjusted).strip()
        if not rebuilt.endswith("."):
            rebuilt += "."
        rebuilt_paragraphs.append(rebuilt)
    return "\n\n".join(rebuilt_paragraphs)


def reduce_overperfect_phrasing(text: str) -> str:
    replacements = {
        "It is a judgment shaped by evidence and carried in plain English.": "It is a judgment shaped by evidence and carried in plain English, maybe plainer than people expect.",
        "The visible pattern is usually simpler than the excuse built around it.": "The visible pattern is usually simpler than the excuse built around it, and that is rarely flattering.",
        "For decision-makers, the task is to name the record, the route, and the discrepancy without performance.": "For decision-makers, the task is to name the record, the route, and the discrepancy without turning it into theater.",
    }
    revised = text
    for source, target in replacements.items():
        revised = revised.replace(source, target)
    return revised


def strip_marketer_corporate_language(text: str) -> str:
    replacements = {
        "optimize": "steady",
        "strategic alignment": "shared understanding",
        "value-add": "real value",
        "unlock": "open",
        "best version": "truest self",
        "trust the process": "face what is true",
        "everything will change": "something has to change",
    }
    revised = text
    for source, target in replacements.items():
        revised = re.sub(rf"\b{re.escape(source)}\b", target, revised, flags=re.IGNORECASE)
    return revised


def replace_term(text: str, source: str, target: str) -> str:
    return re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)


def allowed_by_context(term: str, text: str, context: dict | None, entry: dict | None = None) -> bool:
    if context and term.lower() in {item.lower() for item in context.get("allowed_blacklist_terms", [])}:
        return True
    if not entry:
        return False
    lowered = text.lower()
    for phrase in entry.get("allowed_contexts", []):
        if phrase.lower() in lowered:
            return True
    return False


def preferred_rewrites(term: str, rewrite_map: dict | None = None) -> list[str]:
    mapping = rewrite_map or load_rewrite_map()
    entry = next((item for item in mapping["rewrites"] if item["from"].lower() == term.lower()), None)
    return entry["to"] if entry else []


def merged_lexical_entries(vocabulary_profile: dict | None = None, blacklist: dict | None = None) -> dict[str, dict]:
    profile = vocabulary_profile or load_vocabulary_profile()
    live_blacklist = blacklist or load_live_word_blacklist()
    merged = {}
    for item in profile["discouraged_terms"]:
        merged[item["term"].lower()] = {
            "term": item["term"],
            "status": "discourage",
            "reason": f"Static lexical grounding rule: {item['category']}",
            "occurrence_count": 0,
            "last_updated": "",
            "preferred_substitution": item["preferred_substitution"],
            "category": item["category"],
            "allowed_contexts": [],
        }
    for item in live_blacklist["entries"]:
        merged[item["term"].lower()] = {
            **merged.get(item["term"].lower(), {}),
            **item,
        }
    return merged


def analyze_lexical_grounding(text: str, vocabulary_profile: dict | None = None, context: dict | None = None) -> dict:
    profile = vocabulary_profile or load_vocabulary_profile()
    blacklist = load_live_word_blacklist()
    rewrite_map = load_rewrite_map()
    words = re.findall(r"[A-Za-z']+", text.lower())
    word_count = max(1, len(words))
    abstract_terms = set(profile["term_banks"]["abstract_terms"])
    concrete_terms = set(profile["term_banks"]["concrete_grounding_terms"])
    flagged_terms = []
    blocked_terms = []

    abstract_hits = [word for word in words if word in abstract_terms]
    concrete_hits = [word for word in words if word in concrete_terms]
    for item in merged_lexical_entries(profile, blacklist).values():
        matches = len(re.findall(rf"\b{re.escape(item['term'].lower())}\b", text.lower()))
        if matches:
            context_allowed = item.get("status") == "context_only" and allowed_by_context(item["term"], text, context, item)
            if context_allowed:
                continue
            rewrites = preferred_rewrites(item["term"], rewrite_map)
            status = item.get("status", "discourage")
            if status == "block":
                blocked_terms.append(item["term"])
            flagged_terms.append(
                {
                    "term": item["term"],
                    "count": matches,
                    "status": status,
                    "reason": item.get("reason", ""),
                    "preferred_substitution": rewrites[0] if rewrites else item.get("preferred_substitution", ""),
                    "suggested_rewrites": rewrites,
                }
            )

    abstract_word_ratio = len(abstract_hits) / word_count
    concrete_word_ratio = len(concrete_hits) / word_count
    corporate_ai_term_count = sum(
        item["count"]
        for item in flagged_terms
        if any(token in item["reason"].lower() for token in ["corporate", "ai", "abstract", "institutional"])
    )
    tone_mismatch = (
        abstract_word_ratio > profile["thresholds"]["abstract_word_ratio_warn"]
        and concrete_word_ratio < profile["thresholds"]["concrete_word_ratio_min"]
    )
    lexical_alignment_score = clamp(
        0.42
        + 0.36 * min(concrete_word_ratio / max(profile["thresholds"]["concrete_word_ratio_min"], 0.001), 1.0)
        + 0.1 * float(any(word in words for word in profile["tone_signals"]["lived_grounding_terms"]))
        + 0.08 * float(any(word in words for word in profile["tone_signals"]["cultural_spiritual_terms"]))
        - 0.42 * min(abstract_word_ratio / max(profile["thresholds"]["abstract_word_ratio_fail"], 0.001), 1.0)
        - 0.12 * min(corporate_ai_term_count / 3.0, 1.0)
        - 0.08 * float(tone_mismatch)
    )

    return {
        "lexical_alignment_score": round(clamp(lexical_alignment_score), 3),
        "abstract_word_ratio": round(abstract_word_ratio, 3),
        "concrete_word_ratio": round(concrete_word_ratio, 3),
        "flagged_terms": flagged_terms,
        "blocked_terms": blocked_terms,
        "corporate_ai_term_count": corporate_ai_term_count,
        "tone_mismatch": tone_mismatch,
    }


def enforce_lexical_grounding(draft: str, vocabulary_profile: dict | None = None, context: dict | None = None) -> str:
    profile = vocabulary_profile or load_vocabulary_profile()
    blacklist = load_live_word_blacklist()
    rewrite_map = load_rewrite_map()
    revised = draft
    for item in profile["discouraged_terms"]:
        revised = replace_term(revised, item["term"], item["preferred_substitution"])
    for item in blacklist["entries"]:
        rewrites = preferred_rewrites(item["term"], rewrite_map)
        if item["status"] == "context_only" and allowed_by_context(item["term"], revised, context, item):
            continue
        if item["status"] in {"discourage", "block", "context_only"} and rewrites:
            revised = replace_term(revised, item["term"], rewrites[0])
        elif item["status"] == "block" and not allowed_by_context(item["term"], revised, context, item):
            revised = replace_term(revised, item["term"], "")
    revised = re.sub(r"\s{2,}", " ", revised)
    revised = re.sub(r"\s+([,.!?;:])", r"\1", revised)
    return revised


def ensure_paragraph_first(text: str) -> str:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if len(paragraphs) >= 2:
        return text
    midpoint = max(1, len(text) // 2)
    split_at = text.find(". ", midpoint)
    if split_at == -1:
        split_at = midpoint
    return text[: split_at + 1].strip() + "\n\n" + text[split_at + 1 :].strip()


def grounding_paragraph(mode_id: str) -> str:
    if mode_id == "narrative":
        return (
            "I have seen this kind of truth arrive at a kitchen table and in a church hallway, where the room goes quiet before anybody admits what everyone already knows. "
            "That is part of why I keep the language plain: people deserve words that can stand beside grief, memory, and mercy without pretending to be above them."
        )
    if mode_id == "authority":
        return (
            "I have seen records like this laid out on a scarred table, with one person still defending the story and another finally too tired to keep pretending. "
            "I have also watched that same truth arrive in a church hallway, where mercy and consequence meet before anybody finds polished language for either one. "
            "That lived friction matters, because authority that has never sat with consequence starts sounding institutional long before it sounds wise."
        )
    if mode_id == "utility":
        return (
            "I have learned that plain guidance usually comes from real rooms, not polished decks: a front porch, a school office, a hospital hallway, a kitchen where somebody needs the answer without ceremony. "
            "That kind of grounding keeps the instruction human."
        )
    return (
        "I have seen truths like this surface in ordinary rooms: at a kitchen table, on a front porch, in the moment a family or a team can no longer keep the facts and the story apart. "
        "That lived pressure is part of what gives the words their weight."
    )


def ensure_lived_grounding(text: str, mode_id: str) -> str:
    analysis = analyze_voice_text(text, mode_id)
    if analysis["lived_grounding_score"] >= 0.45 and analysis["cultural_spiritual_grounding_score"] >= 0.2:
        return text
    addition = grounding_paragraph(mode_id)
    if addition not in text:
        return text.strip() + "\n\n" + addition
    return text


def ensure_reflective_anchor(text: str, mode_id: str) -> str:
    analysis = analyze_voice_text(text, mode_id)
    if analysis["reflective_instruction_score"] >= 0.45 and analysis["grounded_emotional_tone"]:
        return text
    addition = "I do not mean that as a slogan. I mean it as the kind of truth people feel in the body before they say it out loud."
    if mode_id == "authority":
        addition = "I do not mean that as a posture. I mean it as the point where evidence and consequence finally touch the same table."
    return text.strip() + "\n\n" + addition


def enforce_voice_identity(draft: str, voice_profile: dict, mode_id: str, final_pass: bool = False) -> str:
    revised = strip_marketer_corporate_language(draft)
    revised = ensure_paragraph_first(revised)
    revised = ensure_lived_grounding(revised, mode_id)
    revised = ensure_reflective_anchor(revised, mode_id)
    if final_pass:
        revised, _ = enforce_thought_visibility(revised)
        revised, _ = enforce_natural_thinking_rhythm(revised)
        revised, _ = preserve_roughness(revised)
        revised = reduce_overperfect_phrasing(revised)
        revised = ensure_sentence_variation(revised)
    return revised


def analyze_voice_text(text: str, mode_id: str | None = None) -> dict:
    lower = text.lower()
    cadence = analyze_cadence(text)
    thought = analyze_thought_visibility(text)
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    lines = [line for line in text.splitlines() if line.strip()]
    bullet_lines = [line for line in lines if line.lstrip().startswith(("-", "*"))]
    bullet_ratio = len(bullet_lines) / max(1, len(lines))
    segments = sentence_segments(text)
    openings = []
    lengths = []
    for segment in segments:
        tokens = re.findall(r"[A-Za-z']+", segment.lower())
        if tokens:
            openings.append(tokens[0])
            lengths.append(len(tokens))
    opening_diversity = len(set(openings)) / max(1, len(openings))
    mean_len = sum(lengths) / len(lengths) if lengths else 0.0
    variance = sum((value - mean_len) ** 2 for value in lengths) / len(lengths) if lengths else 0.0
    rhythm_variation_score = clamp((opening_diversity * 0.55) + min(variance / 60.0, 0.45))

    metaphor_terms = {
        "river", "garden", "seed", "soil", "root", "breath", "hearth", "table",
        "lantern", "weather", "season", "bone", "door", "field", "fire", "shore"
    }
    lived_terms = {
        "mother", "father", "grandmother", "kitchen", "church", "porch", "body",
        "hands", "street", "family", "neighbor", "school", "hospital", "home",
        "table", "garden", "song", "window", "yard", "bench"
    }
    cultural_spiritual_terms = {
        "prayer", "spirit", "church", "ancestor", "grace", "mercy", "ritual",
        "tradition", "community", "faith", "psalm", "altar", "blessing", "choir"
    }
    reflective_terms = {
        "i learned", "i have learned", "what i know", "what changed", "it taught me",
        "i think", "i know", "i remember", "i have seen", "i keep returning"
    }
    calm_certainty_terms = {
        "i know", "what matters", "the truth is", "it is enough", "that is why",
        "i have learned", "i do not need", "what remains"
    }
    marketer_terms = {
        "unlock", "secret", "game-changer", "best version", "crush it", "scale",
        "breakthrough framework", "dominate", "magnetic", "conversion", "high ticket"
    }
    corporate_terms = {
        "stakeholders", "synergy", "leveraging", "optimize", "deliverables", "bandwidth",
        "strategic alignment", "value-add", "enterprise", "scalable", "roadmap"
    }
    generic_motivation_terms = {
        "believe in yourself", "keep moving", "trust the process", "your best life",
        "everything will change", "mindset is everything", "show up as your highest self"
    }
    preachy_terms = {
        "you must", "you should already know", "obviously", "if you were serious",
        "the only people who fail"
    }

    metaphor_hits = sum(1 for token in re.findall(r"[A-Za-z']+", lower) if token in metaphor_terms)
    lived_hits = sum(1 for token in re.findall(r"[A-Za-z']+", lower) if token in lived_terms)
    cultural_hits = sum(1 for token in re.findall(r"[A-Za-z']+", lower) if token in cultural_spiritual_terms)
    reflective_hits = sum(lower.count(term) for term in reflective_terms)
    calm_certainty_hits = sum(lower.count(term) for term in calm_certainty_terms)
    marketer_hits = sum(lower.count(term) for term in marketer_terms)
    corporate_hits = sum(lower.count(term) for term in corporate_terms)
    generic_hits = sum(lower.count(term) for term in generic_motivation_terms)
    preachy_hits = sum(lower.count(term) for term in preachy_terms)

    paragraph_first = len(paragraphs) >= 2 and bullet_ratio <= 0.1
    long_form_signal = len(re.findall(r"[A-Za-z']+", text)) >= 90 or len(paragraphs) >= 2
    grounded_emotional_tone = any(token in lower for token in ["grief", "mercy", "fear", "love", "shame", "care", "hope", "loss", "tired", "quiet", "body"])
    direct_thoughtful_phrasing = any(token in lower for token in ["that is why", "what matters", "i do not mean", "i have learned", "i have seen"])
    meaningful_metaphor = metaphor_hits > 0

    mode_expression_match = True
    if mode_id == "utility":
        mode_expression_match = any(token in lower for token in ["for example", "that is why", "what this means"])
    elif mode_id == "narrative":
        mode_expression_match = any(token in lower for token in ["i remember", "that night", "in the room", "at the table", "hallway"])
    elif mode_id == "authority":
        mode_expression_match = any(token in lower for token in ["record", "evidence", "what the record shows", "audit trail", "that is why"])

    polished_empty_prose_risk = clamp(
        0.28 * (1.0 if not grounded_emotional_tone else 0.0)
        + 0.24 * (1.0 if lived_hits == 0 else 0.0)
        + 0.18 * (1.0 if reflective_hits == 0 else 0.0)
        + 0.16 * (1.0 if cultural_hits == 0 else 0.0)
        + 0.14 * (1.0 if meaningful_metaphor else 0.0) * 0.0
    )

    return {
        "paragraph_count": len(paragraphs),
        "bullet_ratio": round(bullet_ratio, 3),
        "paragraph_first": paragraph_first,
        "long_form_signal": long_form_signal,
        "opening_diversity": round(opening_diversity, 3),
        "rhythm_variation_score": round(rhythm_variation_score, 3),
        "grounded_emotional_tone": grounded_emotional_tone,
        "direct_thoughtful_phrasing": direct_thoughtful_phrasing,
        "meaningful_metaphor": meaningful_metaphor,
        "reflective_instruction_score": round(clamp((reflective_hits / 2.0) + (0.25 if direct_thoughtful_phrasing else 0.0)), 3),
        "lived_grounding_score": round(clamp((lived_hits / 5.0) + (0.15 if grounded_emotional_tone else 0.0)), 3),
        "cultural_spiritual_grounding_score": round(clamp((cultural_hits / 4.0)), 3),
        "calm_certainty_score": round(clamp((calm_certainty_hits / 2.0) + (0.15 if direct_thoughtful_phrasing else 0.0) - (0.2 * preachy_hits)), 3),
        "marketer_voice_risk": round(clamp((marketer_hits / 3.0) + generic_hits * 0.2), 3),
        "corporate_language_risk": round(clamp(corporate_hits / 3.0), 3),
        "generic_motivation_risk": round(clamp(generic_hits / 2.0), 3),
        "list_overuse_risk": round(clamp(bullet_ratio * 3.0), 3),
        "preachy_tone_risk": round(clamp(preachy_hits / 2.0), 3),
        "polished_empty_prose_risk": round(polished_empty_prose_risk, 3),
        "mode_expression_match": mode_expression_match,
        "cadence_naturalness_score": cadence["cadence_naturalness_score"],
        "development_depth_score": cadence["development_depth_score"],
        "compression_score": cadence["compression_score"],
        "compression_flags": cadence["compression_flags"],
        "thought_visibility_score": thought["thought_visibility_score"],
        "experiential_depth_score": thought["experiential_depth_score"],
        "process_visibility_score": thought["process_visibility_score"],
        "experience_presence_score": thought["experience_presence_score"],
        "summarization_flags": thought["summarization_flags"],
        "roughness_score": max(cadence["roughness_score"], thought["roughness_score"]),
        "over_polish_flags": sorted(set(cadence["over_polish_flags"] + thought["over_polish_flags"])),
        "tension_presence_score": round(max(cadence["tension_presence_score"], thought["tension_presence_score"]), 3),
        "signals_present": [
            signal for signal, present in {
                "paragraph_first": paragraph_first,
                "grounded_emotional_tone": grounded_emotional_tone,
                "direct_thoughtful_phrasing": direct_thoughtful_phrasing,
                "meaningful_metaphor": meaningful_metaphor,
                "long_form_signal": long_form_signal,
                "mode_expression_match": mode_expression_match,
                "natural_thinking_rhythm": cadence["cadence_naturalness_score"] >= 0.62,
                "visible_thinking": thought["thought_visibility_score"] >= 0.62,
            }.items() if present
        ],
        "signals_missing": [
            signal for signal, present in {
                "paragraph_first": paragraph_first,
                "grounded_emotional_tone": grounded_emotional_tone,
                "direct_thoughtful_phrasing": direct_thoughtful_phrasing,
                "meaningful_metaphor": meaningful_metaphor,
                "long_form_signal": long_form_signal,
                "mode_expression_match": mode_expression_match,
                "natural_thinking_rhythm": cadence["cadence_naturalness_score"] >= 0.62,
                "visible_thinking": thought["thought_visibility_score"] >= 0.62,
            }.items() if not present
        ],
    }
