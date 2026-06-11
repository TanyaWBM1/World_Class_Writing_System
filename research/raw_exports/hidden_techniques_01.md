elow is a structured set of lesser‑known, underused techniques mapped into system‑oriented logic for a narrative‑systems engine. Each entry is scoped to your target libraries and formatted as compact, implementable blocks.

Burstiness and sentence entropy
Sentence‑length burstiness modulation
Library: cadence_library, sentence_structure_library

Concept: Introduce controlled “spikes” in sentence length (e.g., short–medium–long clusters) instead of uniform length distributions.

Realism gain: Humans tend to cluster complexity (bursts of long sentences inside a paragraph, then resets); this breaks monotonous “average” rhythm that flags synthetic text.

LLM failure mode: LLMs gravitate toward medium‑length, semantically safe sentences; length variance is low and often repetitive.

Failure modes:

Over‑bursting (alternating only ultra‑short and ultra‑long) → staccato rhythm that feels artificial.

No burst memory (each sentence independent) → no paragraph‑level rhythm.

Implementation:

Runtime logic: Maintain a rolling buffer of sentence lengths (token count) per paragraph; sample next‑sentence length from a distribution that preferentially pulls from tails when a “plain” medium‑length cluster has persisted.

Enforcement rule: Require each paragraph to contain at least one sentence below median length and one above.

Validator: Compute rolling standard deviation of sentence length; enforce it to stay above a threshold (e.g., >1.8× expected under a uniform sample).

Schema constraint:

json
"sentence_length_profile": {
  "distribution_type": "bimodal",
  "min_short": 5,
  "max_short": 12,
  "min_long": 25,
  "max_long": 60,
  "burst_window": 4
}
Lexical entropy per sentence
Library: human_texture_library, sentence_structure_library

Concept: Monitor and modulate lexical entropy: variety of wordforms per sentence, avoiding “safe” high‑frequency vocab over‑use.

Realism gain: Human writing exhibits higher wordform entropy; AI tends toward predictable, low‑entropy lexicons.

LLM failure mode: LLMs over‑use training‑corpus frequent words; rare or contextually apt choices are rare.

Failure modes:

“Sprinkled” jargon: inserting rare words in flat, non‑idiomatic frames → feels forced.

No local entropy control: entropy may spike in one sentence and flatline in the next.

Implementation:

Runtime logic: For each sentence, compute Shannon entropy over its wordforms; bias the generator toward synonyms or near‑synonyms if entropy falls below a local threshold.

Enforcement rule: Each sentence must have entropy ≥ ENTROPY_MIN and ≤ ENTROPY_MAX relative to a reference corpus.

Validator: Score per‑sentence entropy and flag sentences where entropy deviates by >2σ from the corpus mean.

Schema constraint:

json
"lexical_entropy": {
  "min": 3.2,
  "max": 5.1,
  "local_window": 3,
  "ref_corpus": "lit_fiction_2000s"
}
Syntactic entropy and clause‑stacking
Library: sentence_structure_library, narrative_pressure_library

Concept: Control how often main clauses are nested with subordinate or participial clauses, varying syntactic depth across sentences.

Realism gain: Humans alternate between simple and complex structures; AI often defaults to simple or uniformly complex syntax.

LLM failure mode: Models tend either toward repeated simple‑sentence rhythms or “run‑on” complexity without paragraph‑level control.

Failure modes:

Over‑stacking: too many clauses in one sentence → difficult parsing.

No depth modulation: all sentences at same clause depth → drone‑like texture.

Implementation:

Runtime logic: Track clause‑depth per sentence; when depth exceeds a threshold, forcibly insert a low‑depth sentence next.

Enforcement rule: No more than N consecutive high‑depth sentences; no more than M consecutive low‑depth sentences.

Validator: Parseoutput to count finite clauses; enforce depth distribution to match a reference (e.g., mean depth 1.8, variance 0.7).

Schema constraint:

json
"clause_depth_policy": {
  "max_depth": 4,
  "max_high_depth_run": 2,
  "max_low_depth_run": 3
}
Discourse‑level variation and pacing
Information‑density bands per paragraph
Library: narrative_pressure_library, cadence_library

Concept: Assign each paragraph an “information band” (high, medium, low) and tune sentence length, clause depth, and lexical density accordingly.

Realism gain: Human writers implicitly modulate how much exposition vs reflection vs action occurs per paragraph; this creates pacing.

LLM failure mode: AI often mixes all densities within a paragraph, flattening narrative pressure.

Failure modes:

All‑high density → info‑dump.

All‑low density → “empty” description or filler.

Implementation:

Runtime logic: Use a stateful paragraph tagger (high/medium/low) influenced by prior narrative pressure; bias sentence length and lexical choice toward that band (e.g., high = short, dense; low = longer, reflective).

Enforcement rule: No more than two consecutive paragraphs of the same band; at least one low‑band paragraph every K narrative units.

Validator: Measure token‑per‑concept ratio (via named entities and predicates) and flag paragraphs where density deviates by >1.5σ from band‑average.

Schema constraint:

json
"info_density_bands": {
  "high": { "min_entities": 4, "max_sentence_length": 20 },
  "medium": { "min_entities": 2, "max_sentence_length": 30 },
  "low": { "min_entities": 0, "max_sentence_length": 50 }
}
Narrative pressure and tension‑gradient modeling
Library: narrative_pressure_library, cadence_library

Concept: Model narrative pressure as a scalar gradient over time (scenes or turns), driving sentence length, clause stacking, and lexical urgency.

Realism gain: Human stories build and release tension; this correlates with shorter, simpler sentences under pressure and longer, descriptive ones in relief.

LLM failure mode: LLMs rarely maintain a coherent tension gradient; pressure spikes are isolated and unsustained.

Failure modes:

Flat pressure → no perceived stakes.

Spikes followed by abrupt drops → whiplash.

Implementation:

Runtime logic: Maintain a running pressure score (e.g., 0–10) updated by events (conflict, revelation, time pressure); scale sentence length inversely and lexical urgency directly to pressure.

Enforcement rule: Pressure must monotonically increase over a scene unless the scene explicitly labels “relief” or “denouement.”

Validator: Compute derivative of pressure per 100 tokens; enforce that it stays within bounds (e.g., −1.0 ≤ slope ≤ +1.5).

Schema constraint:

json
"narrative_pressure_profile": {
  "scene": {
    "min_slope": -0.02,
    "max_slope": 0.08,
    "start": 0.1,
    "end": 0.1
  }
}
Rhetorical texture and voice
Register drift windows
Library: human_texture_library, idiosyncrasy_library

Concept: Define acceptable “drift” ranges for register (formal ↔ informal, narrative ↔ reported) over spans of text.

Realism gain: Writers shift register gradually across scenes; abrupt shifts feel artificial.

LLM failure mode: LLMs often lock into one register or flip registers abruptly.

Failure modes:

No drift → monotone register.

Excessive drift → voice confusion.

Implementation:

Runtime logic: Score each sentence on a formal‑informal axis; enforce that the rolling average over a window of W sentences changes by no more than Δ per step.

Enforcement rule: Register‑score difference between paragraph start and end must be ≤ REGISTER_DRIFT_MAX.

Validator: Flag transitions where the register‑score jump exceeds a threshold across adjacent sentences.

Schema constraint:

json
"register_policy": {
  "score_range": [-3.0, 3.0],
  "max_jump_per_sentence": 0.8,
  "max_jump_per_paragraph": 2.0,
  "ref_style": "literary_third"
}
Signature idiosyncrasy constraints
Library: idiosyncrasy_library, human_texture_library

Concept: Capture and periodically re‑use a small set of character‑specific or author‑specific idiosyncrasies (phrasal fossils, preferred connectors, habitual elisions).

Realism gain: Human writers and characters have stable “fingerprints” (e.g., “Yeah,” “I mean,” “sort of”).

LLM failure mode: Idiosyncrasy is either absent or over‑uniform (every character speaks the same way).

Failure modes:

Over‑use → caricature.

Under‑use → generic voice.

Implementation:

Runtime logic: Maintain a per‑character idiosyncrasy set (e.g., top‑5 phrases, discourse markers); bias dialogue and internal monologue to include at least one item per N turns.

Enforcement rule: Each character must use ≥1 idiosyncrasy per scene and ≤K per sentence.

Validator: Track idiosyncrasy frequencies; raise warnings if they deviate by >2σ from a reference corpus.

Schema constraint:

json
"idiosyncrasy_profile": {
  "character_id": "protagonist_1",
  "phrases": ["you know", "I mean", "sort of", "kinda"],
  "per_turn_min": 1,
  "per_turn_max": 3
}
Free indirect style and perspective modeling
Free indirect discourse (FID) blending rules
Library: human_texture_library, narrative_pressure_library

Concept: Model free indirect style as a weighted blend of narrator lexicon and character lexicon, with a “blend coefficient” per sentence.

Realism gain: FID gives access to character thought while staying in third‑person narration; this is common in modernist and psychological fiction.

LLM failure mode: LLMs either stay in pure narrator voice or switch to direct speech; mixed, seamless FID is rare.

Failure modes:

Over‑blending → confusing whose thoughts are whose.

Under‑blending → no distinct character perspective.

Implementation:

Runtime logic: For each sentence tagged as FID, mix a base narrator lexicon with the current POV character’s lexicon using a coefficient ∈ [0.3, 0.7]; enforce that this coefficient does not flip abruptly.

Enforcement rule: At least one sentence per paragraph must be FID‑tagged in POV‑deep scenes; maximum two consecutive fully‑narrator sentences in a FID‑heavy scene.

Validator: Classify sentences as narrator‑like vs character‑like; flag if FID‑tagged sentences are statistically indistinguishable from narrator‑only.

Schema constraint:

json
"fid_blend_policy": {
  "min_blend": 0.3,
  "max_blend": 0.7,
  "min_fids_per_para": 1,
  "max_consecutive_narrator": 2
}
Scene‑to‑scene residue modeling
Library: narrative_pressure_library, idiosyncrasy_library

Concept: Propagate a “residue” vector (affective, lexical, and referential) from one scene to the next, influencing diction, pacing, and focus.

Realism gain: Human stories carry emotional and lexical residue (e.g., trauma phrasing, repeated motifs) across scenes.

LLM failure mode: LLMs often reset context at scene boundaries; residue is minimal or random.

Failure modes:

No residue → disjointed scenes.

Full carryover → over‑determined themes.

Implementation:

Runtime logic: At scene end, compute a residue vector (top‑k words, sentiment, key concepts) and bias the next scene’s generator to reuse a subset with a decay factor.

Enforcement rule: At least N residue items must appear in the next scene; no residue item may dominate >M% of the next scene.

Validator: Compare cosine similarity between scene embeddings; enforce it to be within a band (e.g., 0.3–0.6).

Schema constraint:

json
"residue_policy": {
  "decay": 0.7,
  "max_items": 8,
  "min_items": 3,
  "min_similarity": 0.3,
  "max_similarity": 0.6
}
Dialogue turn‑taking realism
Turn‑length and overlap policy
Library: dialogue_behavior_library, cadence_library

Concept: Enforce non‑uniform, character‑specific turn lengths and controlled overlaps (interruptions, partial overlaps) instead of perfectly alternating monologues.

Realism gain: Human dialogue is uneven; interruptions, talk‑overs, and truncated turns are common.

LLM failure mode: LLMs default to neat, turn‑by‑turn exchanges with similar lengths.

Failure modes:

No overlap → stilted “theater script” feel.

Constant overlap → chaotic and hard to follow.

Implementation:

Runtime logic: Sample turn length per character from asymmetric distributions; occasionally insert marked interruptions (e.g., speaker_a: "I think—" + speaker_b: "No, you don’t get it—") with a probability tuned to tension level.

Enforcement rule: At least one interruption or partial overlap per X dialogue exchanges; no more than Y consecutive full‑length turns.

Validator: Parse dialogue turns; flag if every turn is cleanly terminated and no overlap markers exist.

Schema constraint:

json
"dialogue_turn_policy": {
  "min_turns_per_char": 2,
  "max_turns_per_char": 5,
  "overlap_prob": 0.18,
  "max_consecutive_clean": 3
}
Dialogue entropy and “noise” modeling
Library: dialogue_behavior_library, human_texture_library

Concept: Inject controlled “noise” tokens (um, uh, stutters, restarts, repetitions) at a tunable rate, tied to character traits and tension.

Realism gain: Human speech is not fully coherent; disfluencies signal thought, emotion, and spontaneity.

LLM failure mode: LLMs produce overly fluent, “written‑for‑performance” dialogue.

Failure modes:

Over‑noise → annoying and hard to read.

Under‑noise → mechanical.

Implementation:

Runtime logic: Per character, maintain a disfluency rate tied to tension and personality; probabilistically insert um/uh, repetitions, or mid‑sentence restarts.

Enforcement rule: Disfluency tokens must occur in ≥D% of turns for anxious characters; ≤E% for confident ones.

Validator: Count disfluency‑type tokens; raise alerts if they fall outside per‑character bands.

Schema constraint:

json
"disfluency_policy": {
  "types": ["um", "uh", "you_know", "like", "repetition"],
  "char_profiles": {
    "nervous": { "min_per_turn": 0.5, "max_per_turn": 2.0 },
    "confident": { "min_per_turn": 0.0, "max_per_turn": 0.5 }
  }
}
Editing techniques and style preservation
Micro‑edit pass: style‑averaging prevention
Library: idiosyncrasy_library, human_texture_library

Concept: Run a post‑generation pass that detects and reverses “style‑averaging” (e.g., smoothing out extreme length, removing idiosyncratic phrases) induced by standard editing heuristics.

Realism gain: Professional edits preserve voice; generic “cleanup” erodes idiosyncrasy.

LLM failure mode: Standard editing steps (repetition removal, sentence‑shortening, synonym‑normalization) homogenize style.

Failure modes:

Over‑preservation → sloppiness.

Under‑preservation → generic voice.

Implementation:

Runtime logic: After each edit pass, compare a sentence’s idiosyncrasy and entropy scores to a reference “un‑edited” version; if scores fall below a threshold, restore or re‑inject idiosyncratic elements.

Enforcement rule: No edit pass may reduce sentence‑level entropy below a per‑character minimum.

Validator: Track entropy and idiosyncrasy per‑character after each edit; flag edits that reduce both by >Δ.

Schema constraint:

json
"edit_safety_policy": {
  "min_entropy_delta": -0.3,
  "max_orthodoxy": 0.2,

## RULESET_EXTRACT
RULE-HT-1: Each paragraph must include controlled sentence-length burstiness rather than a flat medium-length distribution.
RULE-HT-2: Sentence-length variance must stay above the configured lower bound for the active cadence profile.
RULE-HT-3: Lexical entropy per sentence must remain within corpus-relative min/max thresholds.
RULE-HT-4: Clause-depth runs must be bounded; the system may not emit too many consecutive high-depth or low-depth sentences.
RULE-HT-5: Every paragraph must be assigned an information-density band and must conform to that band’s density constraints.
RULE-HT-6: Narrative pressure must evolve within configured slope bounds and may not flatten unintentionally inside pressure-building scenes.
RULE-HT-7: Register drift per sentence and per paragraph must remain inside the allowed drift window for the active voice.
RULE-HT-8: Character or author idiosyncrasies must be present often enough to preserve voice, but not so often that they become caricature.
RULE-HT-9: In POV-deep scenes, free indirect discourse blend must remain within configured narrator/character mixing bounds.
RULE-HT-10: Scene-to-scene residue must carry forward with controlled decay and bounded similarity.
RULE-HT-11: Dialogue must exhibit non-uniform turn lengths and controlled overlap or interruption patterns.
RULE-HT-12: Character disfluency rates must match trait- and tension-specific ranges.
RULE-HT-13: Editing passes may not reduce entropy and idiosyncrasy below the configured preservation floor.
RULE-HT-14: Style-preservation edits must restore voice markers when cleanup operations over-normalize prose.

## OPERATOR_EXTRACT
OP-HT-1: Maintain a rolling paragraph buffer for sentence lengths and trigger burst modulation when medium-length clustering persists.
OP-HT-2: Compute per-sentence lexical entropy and bias generation toward context-appropriate synonymy when entropy is too low.
OP-HT-3: Parse clause depth per sentence and inject compensating low-depth or high-depth sentences when run limits are exceeded.
OP-HT-4: Tag each paragraph with an information-density band and route generation constraints through that band profile.
OP-HT-5: Update a narrative-pressure scalar through each scene and bind cadence decisions to that scalar.
OP-HT-6: Score each sentence on a register axis and block abrupt register jumps beyond configured drift thresholds.
OP-HT-7: Load per-character idiosyncrasy profiles and enforce bounded reuse of signature discourse markers or phrase fossils.
OP-HT-8: Apply FID blend coefficients in POV-deep scenes and keep coefficient changes smooth across adjacent sentences.
OP-HT-9: Compute a residue vector at scene end and bias the next scene with decayed lexical, affective, and conceptual carryover.
OP-HT-10: Sample dialogue turn lengths from character-specific asymmetric distributions and inject bounded overlap markers under tension.
OP-HT-11: Apply disfluency policies by character archetype and tension level.
OP-HT-12: After each edit pass, compare entropy and idiosyncrasy against the pre-edit reference and restore voice markers when needed.
FAILURE_MODE_EXTRACT
FM-HT-1: Cadence flattening through low sentence-length variance and medium-length clustering.
FM-HT-2: Artificial over-bursting that alternates only ultra-short and ultra-long sentences.
FM-HT-3: Low lexical entropy causing safe, generic diction.
FM-HT-4: Clause-depth monotony or unreadable over-stacking.
FM-HT-5: Information-band collapse into all-high-density info-dumps or all-low-density filler.
FM-HT-6: Narrative-pressure flatlining or whiplash spikes.
FM-HT-7: Register monotony or abrupt register flips that confuse voice.
FM-HT-8: Idiosyncrasy absence leading to generic voice.
FM-HT-9: Idiosyncrasy overuse leading to caricature.
FM-HT-10: FID under-blending that erases character perspective.
FM-HT-11: FID over-blending that obscures perspective ownership.
FM-HT-12: Scene-reset behavior with no residue carryover.
FM-HT-13: Dialogue theater-script stiffness with no overlap or interruption.
FM-HT-14: Dialogue over-noise or under-noise relative to character profile.
FM-HT-15: Style averaging during editing that erodes voice.
TEST_CASE_EXTRACT
TC-HT-1: Feed paragraphs with uniform sentence lengths into the cadence validator and verify burstiness violations are raised.
TC-HT-2: Compare low-entropy and corpus-matched sentences and confirm lexical-entropy thresholds separate them.
TC-HT-3: Construct paragraphs with excessive clause stacking and ensure clause-depth run caps trigger.
TC-HT-4: Generate high-density, medium-density, and low-density paragraphs and verify density-band assignment and enforcement.
TC-HT-5: Replay scenes with flat, rising, and whiplash pressure curves and verify pressure-slope validation behavior.
TC-HT-6: Create paragraphs with abrupt formal/informal register jumps and test register-drift detection.
TC-HT-7: Produce dialogue for multiple characters with and without signature markers and verify idiosyncrasy-range checks.
TC-HT-8: Compare narrator-only, balanced-FID, and over-blended FID passages and validate blend-policy scoring.
TC-HT-9: Run adjacent scenes with no residue, bounded residue, and excessive residue carryover and validate similarity-band enforcement.
TC-HT-10: Generate clean alternating dialogue versus interrupted dialogue and ensure overlap-policy checks distinguish them.
TC-HT-11: Evaluate anxious versus confident character dialogue against disfluency-rate bands.
TC-HT-12: Run edit passes that normalize voice and verify post-edit entropy/idiosyncrasy preservation checks catch degradation.
LIBRARY_EXTRACT
cadence_library
sentence_length_burstiness_profile
paragraph_burst_window_policy
information_density_band_profiles
narrative_pressure_curve_policy
dialogue_turn_length_profile
overlap_policy
sentence_structure_library
lexical_entropy_policy
clause_depth_policy
sentence_length_profile
narrative_pressure_library
information_band_state
pressure_gradient_model
scene_residue_policy
fid_scene_depth_policy
human_texture_library
lexical_entropy_guard
register_drift_policy
disfluency_policy
style_averaging_prevention_policy
idiosyncrasy_library
character_idiosyncrasy_profile
author_idiosyncrasy_profile
edit_voice_preservation_policy
dialogue_behavior_library
dialogue_turn_policy
disfluency_profile
interruption_profile