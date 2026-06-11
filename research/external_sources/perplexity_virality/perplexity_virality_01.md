# PERPLEXITY VIRALITY RESEARCH 01

## SOURCE

Perplexity AI Deep Research Output

## PURPOSE

Raw external research on virality mechanisms for ingestion into the v6 Viral Intelligence Layer.

## STATUS

UNPROCESSED

## INGESTION RULE

This file is NOT system-ready.
It must be processed through:
@research-architect  extraction  normalization  library ingestion

## NOTES

* Do NOT copy directly into libraries
* Do NOT use in runtime
* Treat as external knowledge source

---

## CONTENT

# VIRALITY MECHANISMS 01

## MECHANISM 01: HIGH-AROUSAL EMOTION

### DEFINITION
Content that triggers high-activation emotional states (anger, awe, anxiety, inspiration, humor) that increase likelihood of sharing.

### BEHAVIORAL BASIS
High-arousal emotions activate social transmission behavior and increase urgency to share.

### OBSERVABLE SIGNALS
- emotional intensity spikes
- emotionally charged language
- contrast between emotional states
- escalation patterns

### METRICS / PROXIES
- emotion_intensity_score
- emotional_variance
- peak_emotion_delta
- activation_classification (high vs low arousal)

### FAILURE MODES
- decorative emotion (no consequence)
- repeated emotional language without progression
- artificial intensity injection

### VALIDATOR_MAPPING
HighArousalEmotionValidator

---

## MECHANISM 02: HOOK STRENGTH

### DEFINITION
The ability of the opening to create immediate attention via curiosity, clarity, or tension.

### BEHAVIORAL BASIS
Information gap theory  humans seek to resolve uncertainty.

### OBSERVABLE SIGNALS
- clear promise
- curiosity gap
- contradiction
- specificity

### METRICS
- hook_clarity_score
- curiosity_gap_score
- promise_strength
- ambiguity_penalty

### FAILURE MODES
- clickbait (promise not fulfilled)
- vague cleverness
- misleading framing

### VALIDATOR_MAPPING
HookStrengthValidator

---

## MECHANISM 03: IDENTITY RESONANCE

### DEFINITION
Content that reflects the readers identity, beliefs, or lived experience.

### BEHAVIORAL BASIS
People share content to signal identity and values.

### OBSERVABLE SIGNALS
- this is me patterns
- shared struggle language
- belief reinforcement
- group alignment

### METRICS
- identity_alignment_score
- relatability_density
- value_signal_strength

### FAILURE MODES
- generic statements
- forced relatability
- identity bait without substance

### VALIDATOR_MAPPING
IdentityResonanceValidator

---

## MECHANISM 04: SHAREABILITY

### DEFINITION
Ease of extracting and reposting content.

### BEHAVIORAL BASIS
Lower friction  higher sharing probability.

### OBSERVABLE SIGNALS
- short quotable lines
- structured formatting
- clarity and compression

### METRICS
- quotability_score
- compression_ratio
- clarity_score

### FAILURE MODES
- dense writing
- unclear phrasing
- low extraction value

### VALIDATOR_MAPPING
ShareabilityValidator

---

## MECHANISM 05: NOVELTY

### DEFINITION
Non-obvious ideas or reframing of known concepts.

### BEHAVIORAL BASIS
Surprise + coherence increases memorability and sharing.

### OBSERVABLE SIGNALS
- unexpected insight
- reframing
- contradiction of common belief

### METRICS
- novelty_score
- expectation_deviation
- insight_density

### FAILURE MODES
- cliché
- predictable ideas
- random incoherence

### VALIDATOR_MAPPING
NoveltyValidator

---

## RULESET_EXTRACT
- Viral content requires high-arousal emotion OR identity resonance
- Hook must align with payoff
- Novelty must remain coherent
- Shareability depends on clarity + compression

---

## OPERATOR_EXTRACT
- detect_emotional_intensity()
- evaluate_hook_strength()
- measure_identity_alignment()
- extract_quotable_units()
- compute_novelty_score()

---

## FAILURE_MODE_EXTRACT
- clickbait_without_payoff
- emotional_manipulation
- identity_bait
- cliché_repetition
- low_shareability_density

---

## TEST_CASE_EXTRACT
- high_emotion_low_substance  fail
- strong_hook_weak_content  fail
- high_identity_resonance  pass
- novel_insight_high_clarity  pass

---

## LIBRARY_EXTRACT
- evaluation_library  virality_metrics
- failure_mode_library  viral_failure_modes
- benchmark_fixture_library  v6_viral_suite

---

## VALIDATION

After creation, verify:

* Directory exists: research/external_sources/perplexity_virality/
* File exists: perplexity_virality_01.md
* File is NOT empty
* Header is present
