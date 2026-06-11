from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "runtime" / "phrase_system" / "phrase_registry.json"
COOLDOWN_PATH = ROOT / "runtime" / "phrase_system" / "phrase_cooldowns.json"


def load_phrase_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def load_phrase_cooldowns() -> dict:
    return json.loads(COOLDOWN_PATH.read_text(encoding="utf-8"))


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def sentence_segments(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z']+", text.lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))


def phrase_analysis(text: str, grit_level: str | None = None) -> dict:
    registry = load_phrase_registry()
    cooldowns = load_phrase_cooldowns()
    lower = text.lower()
    segments = sentence_segments(text)
    normalized_segments = [normalize(seg) for seg in segments]
    openings = []
    for seg in normalized_segments:
        tokens = seg.split()
        if tokens:
            openings.append(" ".join(tokens[:2]) if len(tokens) >= 2 else tokens[0])

    exact_repetition_count = len(normalized_segments) - len(set(normalized_segments))
    near_duplicate_count = 0
    for index, left in enumerate(normalized_segments):
        left_tokens = set(left.split())
        for right in normalized_segments[index + 1:]:
            similarity = jaccard(left_tokens, set(right.split()))
            if similarity >= cooldowns["near_duplicate_similarity_floor"] and left != right:
                near_duplicate_count += 1

    repeated_openings = {}
    for opening in openings:
        repeated_openings[opening] = repeated_openings.get(opening, 0) + 1
    repeated_openings = {k: v for k, v in repeated_openings.items() if v > cooldowns["repeated_sentence_opening_max"]}

    rhetorical_frame_hits = {}
    for frame in registry["rhetorical_frames"]:
        key = frame.replace("thats", "that's")
        count = lower.count(frame.replace("x", "").replace("y", "").strip())
        if frame == "thats not x thats y":
            count = 1 if ("that's not" in lower or "thats not" in lower) and "that's" not in {"", ""} else 0
        if count:
            rhetorical_frame_hits[key] = count

    signature_phrase_hits = {phrase: lower.count(phrase) for phrase in registry["signature_phrases"] if lower.count(phrase)}

    metaphor_domain_hits = {}
    for domain, terms in registry["metaphor_domains"].items():
        count = sum(lower.count(term) for term in terms)
        if count:
            metaphor_domain_hits[domain] = count

    grit_phrase_hits = {}
    if grit_level:
        for phrase in registry["grit_phrases"].get(grit_level, []):
            count = lower.count(phrase)
            if count:
                grit_phrase_hits[phrase] = count

    signature_phrase_overuse_flag = any(
        count > cooldowns["signature_phrase_max_per_draft"]
        for count in signature_phrase_hits.values()
    )
    metaphor_overuse_risk = clamp(
        sum(max(0, count - cooldowns["metaphor_domain_max_per_draft"]) for count in metaphor_domain_hits.values()) * 0.25
    )
    grit_phrase_reuse_risk = clamp(
        sum(max(0, count - cooldowns["grit_phrase_max_per_draft"]) for count in grit_phrase_hits.values()) * 0.35
    )

    phrase_diversity_score = clamp(
        1.0
        - exact_repetition_count * 0.18
        - near_duplicate_count * 0.12
        - len(repeated_openings) * 0.08
        - (0.25 if signature_phrase_overuse_flag else 0.0)
        - metaphor_overuse_risk
        - grit_phrase_reuse_risk
    )

    return {
        "phrase_diversity_score": round(phrase_diversity_score, 3),
        "exact_repetition_count": exact_repetition_count,
        "near_duplicate_phrase_count": near_duplicate_count,
        "repeated_sentence_openings": repeated_openings,
        "rhetorical_frame_hits": rhetorical_frame_hits,
        "signature_phrase_hits": signature_phrase_hits,
        "metaphor_domain_hits": metaphor_domain_hits,
        "grit_phrase_hits": grit_phrase_hits,
        "grit_phrase_reuse_risk": round(grit_phrase_reuse_risk, 3),
        "metaphor_overuse_risk": round(metaphor_overuse_risk, 3),
        "signature_phrase_overuse_flag": signature_phrase_overuse_flag,
    }


def apply_phrase_controls(text: str, mode_id: str, grit_level: str) -> tuple[str, dict]:
    registry = load_phrase_registry()
    cooldowns = load_phrase_cooldowns()
    revised = text
    substitutions = {
        "that is why": "so",
        "what matters": "the important thing",
        "people rarely change their minds": "people do not change easily",
        "you are going in circles": "you keep returning to the same point",
        "that is not confusion": "this is not confusion",
    }
    applied = []
    for phrase, replacement in substitutions.items():
        if revised.lower().count(phrase) > cooldowns["signature_phrase_max_per_draft"]:
            revised = re.sub(re.escape(phrase), replacement, revised, flags=re.IGNORECASE, count=1)
            applied.append({"type": "signature_cooldown", "phrase": phrase, "replacement": replacement})

    if grit_level:
        grit_phrases = registry["grit_phrases"].get(grit_level, [])
        for phrase in grit_phrases:
            if revised.lower().count(phrase) > cooldowns["grit_phrase_max_per_draft"]:
                revised = re.sub(re.escape(phrase), "", revised, flags=re.IGNORECASE, count=1).strip()
                applied.append({"type": "grit_phrase_cap", "phrase": phrase})

    if mode_id == "narrative" and revised.lower().count("lantern") > cooldowns["metaphor_domain_max_per_draft"]:
        revised = revised.replace("lantern", "small light", 1)
        applied.append({"type": "metaphor_rotation", "from": "lantern", "to": "small light"})

    return revised, {"controls_applied": applied, "post_control_analysis": phrase_analysis(revised, grit_level)}
