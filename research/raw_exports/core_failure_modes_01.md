# LLM Narrative Failure Modes: System-Centric Taxonomy

## 1. Prose Naturalness Failure

### 1.1 Definition  
Text is locally grammatical and semantically plausible but lacks the micro-variability, specificity, and situatedness typical of human prose, producing a statistically smooth yet perceptually “synthetic” surface. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)

**Libraries:** failure_mode_library, abstraction_control_library, cadence_library, evaluation_library  

### 1.2 Failure Mechanics  
- Training optimizes for average likelihood over heterogeneous corpora, biasing outputs toward high-frequency constructions and mid-spectrum style, erasing idiosyncratic micro-choices. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)
- Decoding (low/medium temperature, safety filters) further gravitates toward generic continuations that minimize risk but also texture. [freedomlab](https://freedomlab.com/posts/how-large-language-models-shaped-my-perception-of-writing)
- Lack of embodied or goal-grounded world-models yields descriptive choices that are statistically plausible but weakly tied to concrete, situated context. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)

### 1.3 Why Common Fixes Fail  
- “Add more detail” prompts simply increase generic modifiers and hedging adjectives, amplifying verbosity instead of specificity. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)
- Style prompting with generic “literary” instructions (vivid, engaging, human-like) is absorbed as genre priors and not as concrete constraints. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)
- Post-hoc style transfer or editing passes from the same model collapse differences back toward its internal average. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)

### 1.4 Detection Signals  
- High local fluency metrics but low lexical surprisal variance and low type–token diversity for content words, given topic. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)
- Overuse of generic intensifiers, vague affective adjectives, and pattern templates (“in many ways”, “at the end of the day”, “in a world where”). [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)
- Low density of concrete, observable predicates (actions, physical interactions) compared with abstract descriptors. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)

### 1.5 System Implications  
- Outputs pass surface quality checks but consistently fail subjective “human-ness” evaluations and preference judgments. [arxiv](https://arxiv.org/html/2510.08831v1)
- Fine-tuning on generic “good writing” corpora pushes models further into bland stylistic equilibria. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)

### 1.6 Handling Strategies  

**Runtime logic**  
- Maintain a rolling window of concreteness and lexical surprisal; block continuations if concreteness drops below task-appropriate thresholds.  
- Enforce alternation between abstract and concrete sentences in narrative modes when abstraction ratio exceeds a configurable ceiling.

**Enforcement rules**  
- “Every N sentences, require at least one sentence anchored in physical, observable detail linked to current scene state.”  
- “Reject spans where proportion of vague evaluative adjectives to concrete nouns exceeds threshold K.”  

**Validation systems**  
- Train discriminators for “statistically fluent vs. human-like” prose using human-labeled corpora and use them as gating validators. [arxiv](https://arxiv.org/html/2510.08831v1)
- Use calibration tasks where human-written and model-written paragraphs on the same prompt must be distinguished; measure distance of candidate text to human cluster in embedding space. [arxiv](https://arxiv.org/html/2510.08831v1)

**Schema constraints**  
- At segment level: fields for `situation_anchor`, `sensory_detail[]`, `concrete_action[]` must be non-empty for scenes.  
- Require explicit `micro-decision_tags` (e.g., stance, bias, idiosyncratic perspective) for narratorial paragraphs.

**Human review**  
- Human passes explicitly target “texture density” (original phrasing, concrete specifics, local unpredictability) rather than correctness.  
- Review checklists emphasize deletion of generic filler and replacement with specific, state-grounded detail.

### 1.7 Conversion to System Assets  

**Validator ideas**  
- `ProseConcretenessValidator`: computes concreteness scores, type–token ratios, template-match density; flags over-generic spans.  
- `HumanLikenessDiscriminator`: binary classifier trained on human vs LLM prose for the same prompt. [arxiv](https://arxiv.org/html/2510.08831v1)

**Enforcement rules**  
- `RULE_PROSE_CONCRETENESS_MIN`: `scene.sentences_concrete_ratio >= α`.  
- `RULE_GENERIC_TEMPLATE_CAP`: `generic_template_match_rate <= β`.  

**Benchmark fixtures**  
- Paired prompts with (A) human-paraphrased, specific continuations and (B) generic LLM-like continuations; system must rank A higher.  
- Tasks requiring rewriting “bland but correct” paragraphs into “equally coherent but more concrete and situated” prose, scored by discriminators.

**Library mapping:**  
- failure_mode_library: `prose_naturalness_collapse`  
- abstraction_control_library: `concreteness_ratio_monitor`  
- cadence_library: `local_surprisal_var_tracker`  
- evaluation_library: `human_likeness_disc`, `texture_score_metric`  


***

## 2. Dialogue Realism Failure

### 2.1 Definition  
Dialogue is syntactically correct and contextually relevant but lacks speaker-specific idiolect, turn-taking irregularities, and pragmatic subtext, producing exchanges that feel scripted or exposition-heavy. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)

**Libraries:** failure_mode_library, dialogue_behavior_library, continuity_state_library, evaluation_library  

### 2.2 Failure Mechanics  
- Models optimize for informational clarity and politeness, not for conversational messiness (ellipsis, interruption, misalignment). [linkedin](https://www.linkedin.com/posts/lorimazor_theres-a-lot-of-critique-out-there-about-activity-7326262672398630914-H9fK)
- Training distributions overrepresent edited, cleaned dialogue and underrepresent real conversational transcripts.  
- Lack of persistent, structured character state leads to convergence toward a median politeness and vocabulary profile across speakers. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)

### 2.3 Why Common Fixes Fail  
- “Make it more realistic” prompts introduce profanities or filler words but not consistent pragmatic patterns.  
- Character cards without enforced linkage to token-level generation are treated as soft hints, not state constraints. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)
- Post-edit passes asking the same model to “differentiate voices” often just vary surface ticks (one uses contractions, one does not).

### 2.4 Detection Signals  
- Low divergence between speakers in lexical choice, sentence length distributions, and discourse markers. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)
- Overuse of explicit information stating and absence of implicature, subtext, or conflict markers.  
- Lack of repair phenomena (self-correction, hedging, indirect refusal) in multi-turn segments.  

### 2.5 System Implications  
- Multi-character scenes read as one homogenized voice with character names swapped.  
- Readers and evaluators perceive artificiality even when content matches context. [arxiv](https://arxiv.org/html/2510.08831v1)

### 2.6 Handling Strategies  

**Runtime logic**  
- Maintain per-character style embeddings and enforce minimal cosine distance between them across the scene.  
- Track dialogue acts (question, dodge, deflect, contradict); enforce diversity and character-consistent act patterns.

**Enforcement rules**  
- “Each main character must have stable lexical and syntactic preferences across scenes.”  
- “At least X% of turns must encode non-literal or indirect speech acts when stakes are high.”  

**Validation systems**  
- Dialogue discriminator trained on human conversational corpora vs scripted/LLM dialogue.  
- Clustering-based check: if character utterances cluster poorly by speaker in embedding space, flag homogenization.

**Schema constraints**  
- Dialogue schema includes `speaker_state_id`, `pragmatic_goal`, `hidden_subtext`, `dialogue_act`.  
- Require explicit `conflict_axis` (topic of disagreement or tension) for key scenes.

**Human review**  
- Human operators review a per-character voice report (top n-grams, syntax profile); adjust constraints where convergence occurs.  
- Reviewers focus on whether dialogue reveals character-specific goals and avoidance patterns rather than exposition density.

### 2.7 Conversion to System Assets  

**Validator ideas**  
- `SpeakerDivergenceValidator`: checks per-speaker lexical/syntactic divergence.  
- `PragmaticsCoverageValidator`: evaluates presence and distribution of indirect acts, hedges, and conflict markers.

**Enforcement rules**  
- `RULE_SPEAKER_STYLE_DISTANCE_MIN`: `cos_dist(style_vec[a], style_vec[b]) >= γ`.  
- `RULE_DIALOGUE_ACT_DIVERSITY_MIN`: `dialogue_act_entropy >= δ`.  

**Benchmark fixtures**  
- Multi-speaker scenes with labeled character style profiles; validators must detect synthetic “name-swapping” variants.  
- Pairs of dialogues with same plot function but varying realism; humans label realism, system must align.

**Library mapping:**  
- failure_mode_library: `dialogue_realism_collapse`  
- dialogue_behavior_library: `speaker_state_embedding`, `dialogue_act_tracker`  
- continuity_state_library: `character_voice_state`  
- evaluation_library: `dialogue_realism_disc`  


***

## 3. Sentence Rhythm and Cadence Failure

### 3.1 Definition  
Sentences are coherent but exhibit monotonous rhythm (uniform length, similar clause structure, repeated prosodic patterns) or chaotic variability, causing a detectable “LLM cadence.” [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)

**Libraries:** failure_mode_library, cadence_library, evaluation_library  

### 3.2 Failure Mechanics  
- N-gram and syntax-level generalization favor mid-length, well-punctuated sentences with limited prosodic risk. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)
- Safety and clarity optimization reduces use of sentence fragments, abrupt transitions, or unconventional punctuation that create human-like rhythm.  
- Decoding and RLHF attenuate extremes (very short and very long sentences) leading to compressed variance. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)

### 3.3 Why Common Fixes Fail  
- “Vary sentence length” prompts induce shallow alternation (short–long–short) without truly organic rhythm.  
- Style conditioning on “poetic” or “literary” just increases figurative language, not cadence diversity.  
- Post-hoc edits with the same model preserve its underlying rhythm signature.

### 3.4 Detection Signals  
- Narrow distribution of sentence lengths compared to human baselines for given genre.  
- Overuse of mid-sentence subordinate clauses and similar punctuation patterns (comma-then-“which/that”, parenthetic asides).  
- Low variance in clause types and dependency patterns across paragraphs.

### 3.5 System Implications  
- Text feels oddly smooth, devoid of natural accelerations and slowdowns that signal emphasis and affect.  
- Readers identify the “voice” as LLM-like, even if content is acceptable. [arxiv](https://arxiv.org/html/2510.08831v1)

### 3.6 Handling Strategies  

**Runtime logic**  
- Maintain rolling statistics of sentence length, clause types, punctuation marks; enforce closeness to target distributions per genre.  
- Introduce controlled stochasticity in syntactic templates while respecting semantic constraints.

**Enforcement rules**  
- “Per paragraph, sentence length variance must exceed ε; if not, force structural rewrites.”  
- “Restrict repeated use of identical clause-opening patterns beyond threshold M in a window.”  

**Validation systems**  
- Rhythm classifiers trained to distinguish human vs LLM paragraphs based solely on structural features (length, punctuation, parse trees).  
- Compare candidate cadence histogram to reference author/genre histograms; penalize convergence to global LLM baseline.  

**Schema constraints**  
- Add `cadence_profile` at segment and chapter levels; specify target distributions.  
- Represent paragraphs as sequences of abstract syntax templates, with constraints on repetition.

**Human review**  
- Provide cadence diagnostics (histograms, pattern counts) as part of review dashboard; editors adjust cadence parameters rather than text manually.  

### 3.7 Conversion to System Assets  

**Validator ideas**  
- `CadenceDistributionValidator`: checks sentence length and punctuation distributions against targets.  
- `SyntaxTemplateRepetitionValidator`: tracks recurring parse templates.

**Enforcement rules**  
- `RULE_SENTENCE_LENGTH_VAR_MIN`: `variance(sentence_lengths_window) >= ε`.  
- `RULE_SYNTAX_TEMPLATE_REPEAT_CAP`: `max_template_frequency <= ζ`.  

**Benchmark fixtures**  
- Parallel corpora of human vs LLM prose with cadence labels; validator must separate with high accuracy.  
- Synthetic fixtures where cadence is systematically flattened; system must flag these as violations.

**Library mapping:**  
- failure_mode_library: `cadence_flattening_failure`  
- cadence_library: `sentence_length_monitor`, `syntax_template_tracker`  
- evaluation_library: `cadence_realism_disc`  


***

## 4. Narrative Progression Failure

### 4.1 Definition  
Narrative advances via local plausibility but lacks purposeful escalation, goal-tracking, and causal linkage, leading to “wandering” or episodic progression without coherent arcs. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)

**Libraries:** failure_mode_library, continuity_state_library, abstraction_control_library, evaluation_library  

### 4.2 Failure Mechanics  
- Models optimize for next-token plausibility, not for long-horizon control of story state or global objectives. [arxiv](https://arxiv.org/abs/2602.06176)
- Absence of explicit narrative control state (goals, unresolved tensions) produces open-loop drift toward generic events. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)
- Safety and alignment training favor conflict-smoothing responses, muting antagonism and stakes.  

### 4.3 Why Common Fixes Fail  
- “Outline then write” prompts generate outlines that are not used as hard constraints during generation.  
- Chain-of-thought style “reasoning” about plot is not tethered to decoding decisions robustly, leading to drift. [arxiv](https://arxiv.org/abs/2602.06176)
- Longer context windows alone do not solve state tracking; model still lacks a control process for goal maintenance. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)

### 4.4 Detection Signals  
- Weak or absent mapping from early foreshadowing to later payoff.  
- Flat graphs of tension/stakes across chapters; no identifiable act structure.  
- Inconsistent or forgotten sub-goals, side characters, or unresolved questions.

### 4.5 System Implications  
- Readers report boredom or a sense that “nothing adds up,” despite continuous events.  
- Difficult to use LLMs for long-form narrative without heavy external scaffolding. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)

### 4.6 Handling Strategies  

**Runtime logic**  
- Maintain explicit `narrative_state` including goals, conflicts, promises, and act position; gate generation against this state.  
- Periodically re-derive next-scene objectives from `narrative_state` and enforce them via constraints.

**Enforcement rules**  
- “Each scene must advance at least one active goal or increase at least one unresolved tension.”  
- “Every foreshadowed element must either be resolved or explicitly subverted by narrative end.”  

**Validation systems**  
- Narrative-structure validators that infer arcs and goal trajectories, comparing them to schema (e.g., three-act, mystery, etc.).  
- Consistency checkers that align early promises with later scenes to detect dropped threads.

**Schema constraints**  
- Story graph schema: nodes = events; edges = causal or goal-related links; minimum density and connectivity enforced.  
- Annotation fields for `scene_goal`, `stakes_delta`, `unresolved_questions[]`.  

**Human review**  
- Humans interact with story graph visualizations, marking missing payoffs or unmotivated detours; system updates constraints accordingly.  

### 4.7 Conversion to System Assets  

**Validator ideas**  
- `NarrativeGoalProgressValidator`: checks that each scene modifies at least one narrative goal.  
- `PromisePayoffValidator`: tracks introduced promises and verifies resolution or deliberate subversion.

**Enforcement rules**  
- `RULE_SCENE_GOAL_REQUIRED`: `scene.scene_goal != null`.  
- `RULE_PROMISE_RESOLUTION_RATE`: `resolved_promises / introduced_promises >= θ`.  

**Benchmark fixtures**  
- Stories with deliberately removed climaxes or payoffs; validators must flag arc collapse.  
- Synthetic narratives with shuffled scenes to test detection of broken causal chains.

**Library mapping:**  
- failure_mode_library: `narrative_drift_failure`  
- continuity_state_library: `narrative_goal_state`, `promise_registry`  
- abstraction_control_library: `tension_curve_model`  
- evaluation_library: `arc_coherence_metric`  


***

## 5. Long-Form Coherence Failure

### 5.1 Definition  
Text maintains local coherence but accumulates contradictions, topic drift, and structural inconsistencies over long horizons, especially beyond the window of active control. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)

**Libraries:** failure_mode_library, continuity_state_library, evaluation_library  

### 5.2 Failure Mechanics  
- Context windows are used as raw text, not as structured state; important information becomes buried and effectively forgotten.  
- Models lack robust self-consistency, changing decisions when prompts are rephrased or partial outputs are re-fed. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)
- No closed-loop control: generation is largely open-loop with rare or weak external corrections. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)

### 5.3 Why Common Fixes Fail  
- Larger context windows only delay failure; they do not provide mechanisms for state summarization and enforcement. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)
- Naive retrieval of earlier segments retrieves irrelevant or noisy context and overwhelms decoding.  
- Self-check prompts (“verify consistency”) run on the same model frequently miss subtle contradictions.

### 5.4 Detection Signals  
- Increasing rate of factual or state contradictions with distance from starting chapters.  
- Drift in key entities’ attributes, motivations, or relationships.  
- Substantial semantic overlap between distant segments where repetition is unintended.

### 5.5 System Implications  
- Long documents must be heavily curated by humans to be usable.  
- Reliability decreases non-linearly with length, limiting autonomy for long-form writing.

### 5.6 Handling Strategies  

**Runtime logic**  
- Maintain `continuity_state` as compact structured memory (entities, facts, relationships, commitments), updated incrementally.  
- Gate generation through continuity checks that reject proposals violating `continuity_state` constraints.

**Enforcement rules**  
- “No segment may assert a fact in direct contradiction with the continuity state without explicitly marking it as retcon or unreliable narration.”  
- “Entities’ core attributes are immutable unless an explicit state-change event is logged.”  

**Validation systems**  
- Cross-document contradiction detection using NLI (entailment/contradiction models) across key facts.  
- Segment-level drift detectors comparing semantic embeddings to prior state summaries.

**Schema constraints**  
- Entity schemas with canonical attributes, history logs, and invariants.  
- Chapter schemas referencing `continuity_state_version_id` used for generation.

**Human review**  
- Human curators inspect continuity dashboards showing entity timelines and conflict alerts rather than scanning full text.  

### 5.7 Conversion to System Assets  

**Validator ideas**  
- `ContinuityNLIValidator`: runs entailment checks between new statements and continuity state.  
- `EntityAttributeDriftValidator`: tracks attribute changes and flags unexplained shifts.

**Enforcement rules**  
- `RULE_ENTITY_INVARIANT_ENFORCED`: `violated_invariants == 0`.  
- `RULE_CONTINUITY_CONTRADICTION_CAP`: `contradiction_score_window <= κ`.  

**Benchmark fixtures**  
- Long stories with inserted contradictions in late chapters; validators must find them.  
- Technical documents with intentionally inconsistent definitions across sections.

**Library mapping:**  
- failure_mode_library: `long_form_coherence_failure`  
- continuity_state_library: `entity_registry`, `fact_invariant_store`  
- evaluation_library: `coherence_over_distance_metric`  


***

## 6. Abstraction and Over-Explanation Failure

### 6.1 Definition  
Model defaults to abstract commentary, meta-explanation, and restatement, crowding out specific, situational content and implicit meaning. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)

**Libraries:** failure_mode_library, abstraction_control_library, evaluation_library  

### 6.2 Failure Mechanics  
- LLMs are trained heavily on expository and explanatory text, over-weighting high-level descriptions and explicit reasoning. [arxiv](https://arxiv.org/abs/2602.06176)
- Safety and clarity alignment promote “explain everything” behavior, reducing reliance on reader inference.  
- Abstraction is cheap to generate and reuses frequent patterns, making it high-probability compared with specific, risky detail. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)

### 6.3 Why Common Fixes Fail  
- “Be more subtle” or “show, don’t tell” prompts are interpreted as stylistic hints, not strong constraints.  
- Temperature or sampling changes only affect surface wording, not the preference for abstract vs concrete moves.  
- Length limits lead the model to compress via abstract summaries rather than selective specificity.

### 6.4 Detection Signals  
- High ratio of meta-commentary sentences to concrete action or sensory sentences.  
- Frequent phrases indicating meta stance (“in other words”, “this means that”, “essentially”).  
- Low density of implied meaning; most inferences are explicitly spelled out.

### 6.5 System Implications  
- Narratives and essays feel didactic, overclarified, and less engaging.  
- Critical argumentation becomes circular: models generate claims and re-explain them rather than advancing content. [arxiv](https://arxiv.org/html/2602.21045v1)

### 6.6 Handling Strategies  

**Runtime logic**  
- Track an `abstraction_level` feature per sentence; reject over-threshold sequences of high-abstraction sentences.  
- Enforce quota of implicit vs explicit statements: require some key implications to remain unstated.

**Enforcement rules**  
- “For every abstract evaluative statement, require at least one adjacent concrete grounding sentence.”  
- “Limit consecutive meta-explanation sentences to N.”  

**Validation systems**  
- Abstract–concrete classifiers per sentence trained on annotated corpora.  
- Argument depth metrics that penalize redundant paraphrase of the same point without new evidence.

**Schema constraints**  
- Separate fields for `abstract_claims[]` and `concrete_support[]`; enforce non-empty support for claims.  
- Metadata flags for `implicit_inference_points[]` that must not be explicitly described.

**Human review**  
- Humans can promote or demote abstraction levels globally (e.g., slider), with the system regenerating at new constraint settings.  

### 6.7 Conversion to System Assets  

**Validator ideas**  
- `AbstractionDensityValidator`: computes abstraction ratio over windows.  
- `MetaExplanationPatternValidator`: detects overuse of meta phrases.

**Enforcement rules**  
- `RULE_ABSTRACTION_RATIO_MAX`: `abstract_sentences / total_sentences <= λ`.  
- `RULE_META_SENTENCE_RUN_CAP`: `max_consecutive_meta <= μ`.  

**Benchmark fixtures**  
- Paired passages (over-explained vs balanced) labeled by humans; validator calibrated to human preferences.  
- Argument tasks where over-explaining reduces score; system must optimize for concision and specificity.

**Library mapping:**  
- failure_mode_library: `over_abstraction_failure`  
- abstraction_control_library: `abstraction_level_tracker`  
- evaluation_library: `abstraction_balance_metric`  


***

## 7. Semantic Repetition Without Phrase Repetition

### 7.1 Definition  
Model avoids exact phrase repetition but repeatedly reasserts the same semantic content, leading to circularity and perceived padding. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)

**Libraries:** failure_mode_library, abstraction_control_library, evaluation_library  

### 7.2 Failure Mechanics  
- LLMs are penalized for verbatim reuse (via decoding penalties) but not for semantic redundancy.  
- Coherence objectives favor linking back to prior content, and the model interprets this as restating points with minor lexical variation. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)
- Lack of explicit discourse plan means the model does not track which propositions have already been “cashed out.”

### 7.3 Why Common Fixes Fail  
- “Avoid repetition” is applied as n-gram-level or phrase-level constraint, not conceptual tracking.  
- Length constraints encourage expanding existing points rather than introducing new ideas.  
- Self-critique prompts (“have I repeated myself?”) rely on the same model’s embeddings and often miss more subtle redundancy.

### 7.4 Detection Signals  
- High semantic similarity between different paragraphs or sections, as measured in embedding space.  
- Introduced claims are paraphrased multiple times without new evidence or refinement.  
- Discourse structure shows repeated re-entry into the same topic nodes.

### 7.5 System Implications  
- Documents appear padded or “spun,” undermining trust in content density.  
- Automated evaluation metrics focused on surface features do not capture the redundancy.

### 7.6 Handling Strategies  

**Runtime logic**  
- Maintain rolling representation of asserted propositions; reject candidate sentences that exceed semantic similarity threshold to existing assertions.  
- Require that each major segment contributes new propositions or relations to the discourse graph.

**Enforcement rules**  
- “No more than R semantically redundant sentences per K-sentence window.”  
- “Each section must introduce at least one new claim, evidence item, or counterpoint relative to prior sections.”  

**Validation systems**  
- Proposition-level clustering of sentences; high cluster density without structural role differences triggers flags.  
- Argumentation validators that track new vs re-used premises.

**Schema constraints**  
- `proposition_id`s associated with sentences; system must either reference or extend them, not re-assert them verbatim.  
- `section_novelty_score` field that must exceed threshold.

**Human review**  
- User-facing views highlight repeated propositions; humans can request compression or deletion passes constrained by state.

### 7.7 Conversion to System Assets  

**Validator ideas**  
- `SemanticRedundancyValidator`: embedding-based similarity checks over windows.  
- `DiscourseNoveltyValidator`: monitors rate of new propositions.

**Enforcement rules**  
- `RULE_SEMANTIC_REDUNDANCY_CAP`: `redundant_sentence_ratio <= ν`.  
- `RULE_SECTION_NOVELTY_MIN`: `section_novelty_score >= ξ`.  

**Benchmark fixtures**  
- Synthetic documents with semantic “spin” layers added; validators must detect inflated redundancy.  
- Human-annotated corpora marking redundant vs novel sentences.

**Library mapping:**  
- failure_mode_library: `semantic_redundancy_failure`  
- abstraction_control_library: `proposition_graph_tracker`  
- evaluation_library: `semantic_density_metric`  


***

## 8. Emotional Flattening

### 8.1 Definition  
Emotional content becomes uniform, polite, and moderated, lacking intensity variation, idiosyncratic affect, and credible negative or risky emotions. [freedomlab](https://freedomlab.com/posts/how-large-language-models-shaped-my-perception-of-writing)

**Libraries:** failure_mode_library, abstraction_control_library, continuity_state_library, evaluation_library  

### 8.2 Failure Mechanics  
- Alignment and safety training penalize extremes of affect (rage, despair, vindictiveness), biasing toward neutral or mildly positive emotion. [freedomlab](https://freedomlab.com/posts/how-large-language-models-shaped-my-perception-of-writing)
- Models favor emotion words and generic descriptions over embodied emotional behavior.  
- No explicit affective state tracking across scenes, causing mood resets and averaging.

### 8.3 Why Common Fixes Fail  
- “Make it more emotional” prompts increase emotional adjectives instead of deepening affect through situation and behavior.  
- Attempts to inject conflict are moderated by refusal and safety layers that avoid harmful depictions.  
- Post-hoc “tone adjustments” from the same model re-homogenize affect.

### 8.4 Detection Signals  
- Narrow distribution of valence and arousal scores across large spans.  
- Frequent use of generic emotion descriptors (“she felt sad”, “he was happy”) without specific triggers or manifestations.  
- Inconsistent emotional trajectories (characters snap between states without proportional cause).

### 8.5 System Implications  
- Readers perceive characters as emotionally one-dimensional or oddly calm.  
- Dramatic scenes do not feel impactful despite correct events occurring.

### 8.6 Handling Strategies  

**Runtime logic**  
- Maintain per-character affective trajectories as continuous variables; enforce continuity and proportional change.  
- Use affect-level constraints at scene level (target valence/arousal) and penalize deviations from intended trajectory.

**Enforcement rules**  
- “For high-stakes scenes, require at least one behaviorally grounded emotional reaction per focal character.”  
- “Restrict use of generic emotional adjectives without accompanying behavioral or situational grounding.”

**Validation systems**  
- Emotion classifiers applied sentence-by-sentence; aggregate to detect flattening.  
- Trajectory analysis comparing narrative affect curves to genre norms (e.g., thriller vs slice-of-life).

**Schema constraints**  
- Scene-level fields: `target_affect_profile`, `emotion_events[]`.  
- Character-level state: `current_emotion`, `recent_triggers[]`, `coping_style`.

**Human review**  
- Review dashboards show affect curves and identify flat regions for targeted regeneration.  

### 8.7 Conversion to System Assets  

**Validator ideas**  
- `AffectVarianceValidator`: tracks variance of valence/arousal over segments.  
- `GenericEmotionPhraseValidator`: flags generic emotion phrases without concrete support.

**Enforcement rules**  
- `RULE_AFFECT_VARIANCE_MIN`: `affect_variance_window >= ρ`.  
- `RULE_GENERIC_EMOTION_CAP`: `generic_emotion_rate <= σ`.  

**Benchmark fixtures**  
- Stories with flattened affect vs human-edited versions with richer trajectories; validators must favor the latter.  
- Scenarios annotated with expected affect curves.

**Library mapping:**  
- failure_mode_library: `emotional_flattening_failure`  
- abstraction_control_library: `affect_curve_model`  
- continuity_state_library: `character_affect_state`  
- evaluation_library: `affect_dynamics_metric`  


***

## 9. Continuity and Memory Failures

### 9.1 Definition  
Intra-document memory breaks: inconsistent facts, forgotten subplots, or misapplied prior context, even when information appears in the prompt or context window. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)

**Libraries:** failure_mode_library, continuity_state_library, evaluation_library  

### 9.2 Failure Mechanics  
- Models treat context as unstructured text rather than as prioritized state; important items are not tagged or weighted. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)
- Self-consistency is weak; slight changes in prompts or intermediate steps change final answers. [arxiv](https://arxiv.org/abs/2602.06176)
- No explicit mechanism for long-term memory consolidation into stable state representations. [reddit](https://www.reddit.com/r/ControlTheory/comments/1poncp8/why_longhorizon_llm_coherence_is_a_control/)

### 9.3 Why Common Fixes Fail  
- “Remember X” instructions are soft and easily overridden by more recent or stronger statistical patterns.  
- External memory systems that just append notes to context do not provide structured constraints during decoding.  
- Self-critique checks after generation are expensive and can miss subtle continuity errors.

### 9.4 Detection Signals  
- Contradictions about character backstory, timeline, or world rules.  
- Shifts in point of view or narrative mode that break prior commitments.  
- Inconsistent use of invented terminology or magic/technology rules.

### 9.5 System Implications  
- Fictional universes and technical documents break internal logic, reducing trust and engagement.  
- Tools built on LLMs require heavy human curation for continuity.

### 9.6 Handling Strategies  

**Runtime logic**  
- Treat continuity as a separate, structured state store, updated and validated at segment boundaries.  
- Apply hard constraints from continuity state during decoding (e.g., masked or penalized contradictory tokens).  

**Enforcement rules**  
- “Core canon facts cannot change unless explicitly updated via a state-change event, which must be narrated.”  
- “New statements about world rules must be checked against existing rule sets for compatibility.”

**Validation systems**  
- NLI and rule-based systems for detecting contradictions between new segments and continuity state.  
- Ontology-based validators that check domain-specific invariants (e.g., physical laws, magic rules).

**Schema constraints**  
- `world_canon` object with immutable or conditionally mutable entries.  
- `continuity_assertions[]` per segment, explicitly mapped to canon entries.

**Human review**  
- Human continuity editors operate directly on `world_canon` and entity timelines, not unstructured text.  

### 9.7 Conversion to System Assets  

**Validator ideas**  
- `WorldCanonConsistencyValidator`.  
- `TermUsageConsistencyValidator` for invented terms and rules.

**Enforcement rules**  
- `RULE_CANON_NO_IMPLICIT_OVERRIDE`.  
- `RULE_TERM_DEFINITION_STABILITY`: `definitions_conflict == 0`.  

**Benchmark fixtures**  
- Fantasy or SF settings with intentionally altered rules in later chapters; validators must catch the inconsistencies.  
- Technical manuals with conflicting protocol descriptions.

**Library mapping:**  
- failure_mode_library: `continuity_memory_failure`  
- continuity_state_library: `world_canon_store`, `timeline_registry`  
- evaluation_library: `continuity_integrity_metric`  


***

## 10. Style Homogenization Across Outputs

### 10.1 Definition  
Across different projects and prompts, outputs collapse into a narrow band of stylistic patterns, eroding distinctiveness and making texts recognizably “LLM-like.” [arxiv](https://arxiv.org/html/2510.08831v1)

**Libraries:** failure_mode_library, abstraction_control_library, cadence_library, evaluation_library  

### 10.2 Failure Mechanics  
- Pretraining on blended corpora produces a dominant “average style” basin. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)
- RLHF and safety further compress style toward polite, expository, neutral voice.  
- Lack of persistent author-level style state; each generation restarts from global LLM priors.

### 10.3 Why Common Fixes Fail  
- Per-prompt style instructions add superficial features but do not carve stable new basins.  
- Few-shot style conditioning is unstable under longer generation and revision cycles. [reddit](https://www.reddit.com/r/WritingWithAI/comments/1ne4c29/when_ai_prose_feels_statistically_correct_but/)
- Using the same LLM for drafting and revision re-applies homogenizing gradients.

### 10.4 Detection Signals  
- Cross-document similarity of stylistic features (cadence, lexical choice, discourse markers) regardless of nominal author.  
- Convergence to LLM signature patterns under repeated revision cycles.  
- Low inter-project style variance compared with human-author baselines. [arxiv](https://arxiv.org/html/2510.08831v1)

### 10.5 System Implications  
- Systems cannot support distinct author brands or house styles reliably.  
- Detection of AI authorship becomes easier over time, even with content variation. [arxiv](https://arxiv.org/html/2510.08831v1)

### 10.6 Handling Strategies  

**Runtime logic**  
- Bind outputs to `author_style_state` objects learned or specified at system level, overriding global priors.  
- Penalize drift from style state during generation and revision.

**Enforcement rules**  
- “Distance between current style metrics and target author style must remain below threshold.”  
- “Revision passes may not reduce style divergence between authors below global minimum.”  

**Validation systems**  
- Style fingerprinting models that compute distance between output and target author/genre corpora.  
- Diversity metrics across corpus of outputs; homologous outputs trigger system-level alerts.

**Schema constraints**  
- `author_style_id` required; includes cadence profile, lexical preferences, syntactic biases.  
- `revision_style_guardrails` specifying invariants that revisions cannot break.

**Human review**  
- Humans validate style fingerprints periodically and adjust author profiles; they review style drift reports instead of raw content.  

### 10.7 Conversion to System Assets  

**Validator ideas**  
- `AuthorStyleFingerprintValidator`.  
- `CorpusStyleDiversityValidator`.

**Enforcement rules**  
- `RULE_STYLE_DISTANCE_MAX`: `style_distance(output, author_profile) <= ω`.  
- `RULE_CORPUS_STYLE_DIVERSITY_MIN`: `corpus_style_variance >= ψ`.  

**Benchmark fixtures**  
- Corpora with multiple authors; system must assign outputs correctly and preserve style distinctions over revisions.  
- Stress tests where repeated revisions attempt to converge styles; validators must detect erosion.

**Library mapping:**  
- failure_mode_library: `style_homogenization_failure`  
- abstraction_control_library: `author_style_profile_store`  
- cadence_library: `author_cadence_profile`  
- evaluation_library: `style_fingerprint_metric`  


***

## 11. Author Voice Erosion Under Revision

### 11.1 Definition  
Initial drafts with distinctive voice are progressively normalized during AI-assisted revision, losing idiosyncratic traits while retaining content. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)

**Libraries:** failure_mode_library, abstraction_control_library, evaluation_library  

### 11.2 Failure Mechanics  
- Revision prompts focus on clarity, correctness, and “better writing,” which align with model’s average style basin. [dl.acm](https://dl.acm.org/doi/full/10.1145/3706598.3713559)
- Model lacks representation of “voice invariants” it must preserve, treating all deviations as noise to correct.  
- Iterative passes compound small stylistic edits into large shifts.

### 11.3 Why Common Fixes Fail  
- “Preserve my voice” instructions are vague and conflict with clarity/correctness directives.  
- Using the same model for critique and rewrite encourages self-convergence.  
- Style locks at surface level (e.g., keep first-person) do not preserve deeper rhythmic or lexical traits.

### 11.4 Detection Signals  
- Measurable drift in style features from initial human draft to final output.  
- Convergence toward global LLM style metrics after multiple passes.  
- Human annotators detect loss of individuality while core meaning remains. [arxiv](https://arxiv.org/html/2510.08831v1)

### 11.5 System Implications  
- Tools inadvertently erase authors’ identities over time.  
- Professional workflows become dependent on manual voice restoration.

### 11.6 Handling Strategies  

**Runtime logic**  
- Treat initial human draft as reference style; constrain subsequent edits to minimize stylistic distance.  
- Separate “content edits” and “style edits,” and strictly bound style changes.

**Enforcement rules**  
- “Edits must not change predefined voice features beyond tolerance (lexical rarity, cadence, sentence patterning).”  
- “Revision passes allowed to alter only content-specific spans, not baseline rhythm patterns.”

**Validation systems**  
- Style-drift detectors comparing before/after at each revision step.  
- Voice preservers that highlight where stylistic fingerprints are weakened.

**Schema constraints**  
- `voice_anchor_text` stored per project.  
- `revision_intent` field that specifies whether style can be touched.

**Human review**  
- Humans approve or reject style-affecting edits highlighted by drift analysis.

### 11.7 Conversion to System Assets  

**Validator ideas**  
- `StyleDriftValidator`.  
- `VoiceInvariantPreservationValidator`.

**Enforcement rules**  
- `RULE_VOICE_DRIFT_CAP`: `style_distance(after, voice_anchor) <= χ`.  
- `RULE_REVISION_SCOPE_STYLE_LOCK`: if `revision_intent != "style"`, forbid stylistic changes.

**Benchmark fixtures**  
- Human drafts with distinctive voice; revision tasks where acceptable systems preserve voice metrics.  
- Synthetic cases where LLM revisions destroy voice; validators must flag.

**Library mapping:**  
- failure_mode_library: `voice_erosion_failure`  
- abstraction_control_library: `voice_anchor_store`  
- evaluation_library: `style_drift_metric`  


***

## 12. Genre Flattening

### 12.1 Definition  
Different genres (mystery, essay, sci-fi, romance) are realized through the same generic expository patterns, with weak adherence to genre-specific structures, tropes, and discourse moves. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)

**Libraries:** failure_mode_library, abstraction_control_library, continuity_state_library, evaluation_library  

### 12.2 Failure Mechanics  
- Models act as “genre machines” that rely on broad genre markers but not fine-grained structural constraints. [meresophistry.substack](https://meresophistry.substack.com/p/the-curious-question-of-ai-written)
- Training aggregates diverse genre realizations, producing diluted, averaged genre signatures.  
- Safety and RLHF discourage darker or more transgressive genre conventions.

### 12.3 Why Common Fixes Fail  
- “Write in genre X” prompts add surface markers (setting, terminology) rather than true structural differences.  
- Example-based conditioning is quickly forgotten in long outputs.  
- Post-hoc “genreization” edits mostly introduce clichés.

### 12.4 Detection Signals  
- Low discriminability of outputs by genre classifier trained on human texts.  
- Similar cadence, abstraction level, and narrative progression across genres.  
- Absence or weak presence of genre-specific features (clue planting in mystery, sense-of-wonder in SF, etc.).

### 12.5 System Implications  
- Hard to deliver genre-faithful narratives; readers perceive sameness across projects.  
- Downstream tools (e.g., recommendation) misclassify or undervalue such works.

### 12.6 Handling Strategies  

**Runtime logic**  
- Bind each project to a `genre_schema` with explicit structural and stylistic requirements.  
- Enforce adherence to genre-specific arcs, beats, and motif distributions.

**Enforcement rules**  
- “Mystery genre must include clue–red-herring–reveal structures with specific density.”  
- “Horror requires minimum suspense curve and dread markers; romance requires relationship tension arcs.”

**Validation systems**  
- Genre classifiers and structure analyzers trained on human corpora.  
- Beat-detection systems checking for presence and placement of genre-specific beats.

**Schema constraints**  
- `genre_id` mandatory; `genre_beat_map` specifying required beats and constraints.  
- Scene annotations include `genre_function` (e.g., clue drop, red herring, meet-cute).

**Human review**  
- Genre experts inspect beat maps rather than raw prose, adjusting constraints when needed.

### 12.7 Conversion to System Assets  

**Validator ideas**  
- `GenreConformityValidator`.  
- `GenreBeatCoverageValidator`.

**Enforcement rules**  
- `RULE_GENRE_BEAT_COVERAGE_MIN`.  
- `RULE_GENRE_SIGNATURE_FEATURES_MIN`.

**Benchmark fixtures**  
- Human-annotated genre corpora with beat labels; outputs compared for conformity.  
- LLM-generated flattened outputs vs curated genre-faithful variants.

**Library mapping:**  
- failure_mode_library: `genre_flattening_failure`  
- abstraction_control_library: `genre_schema_store`  
- continuity_state_library: `genre_beat_state`  
- evaluation_library: `genre_conformity_metric`  


***

## 13. Prompt Sensitivity / Output Fragility

### 13.1 Definition  
Small, semantically neutral changes in prompt wording or ordering cause large, unpredictable changes in output style, content, or coherence. [arxiv](https://arxiv.org/abs/2602.06176)

**Libraries:** failure_mode_library, evaluation_library  

### 13.2 Failure Mechanics  
- LLMs exhibit brittle decision surfaces; slight prompt perturbations alter early token choices that cascade through generation. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)
- No robust semantic representation of “task intent” separate from literal prompt wording.  
- Over-reliance on few-shot exemplars and instruction phrasing as anchor points.

### 13.3 Why Common Fixes Fail  
- Prompt engineering heuristics mitigate individual cases but do not provide global robustness.  
- System prompts and templates reduce variance but often intensify homogenization instead.  
- Self-consistency approaches (multiple samples) can average out fragility but at high cost.

### 13.4 Detection Signals  
- Large variance in outputs across paraphrased prompts that preserve semantic task.  
- Disagreement between model-as-judge evaluations for small input changes. [dl.acm](https://dl.acm.org/doi/10.1145/3746059.3747677)
- Frequent contradictions in reasoning tasks under prompt perturbations. [arxiv](https://arxiv.org/abs/2602.06176)

### 13.5 System Implications  
- Hard to guarantee stable behavior in production; minor UX changes can break outputs.  
- Regression testing becomes complex and brittle.

### 13.6 Handling Strategies  

**Runtime logic**  
- Normalize prompts into structured task representations before generation.  
- For critical tasks, generate multiple candidates from paraphrased prompts and enforce consensus.

**Enforcement rules**  
- “Outputs must remain within acceptable variation bounds across standardized prompt perturbation set.”  
- “Reject candidate model configurations that fail robustness tests beyond threshold.”

**Validation systems**  
- Prompt-robustness benchmarks measuring consistency across paraphrase sets. [arxiv](https://arxiv.org/abs/2602.06176)
- LLM-as-judge evaluation frameworks that explicitly test multiple plausible user intents. [dl.acm](https://dl.acm.org/doi/10.1145/3746059.3747677)

**Schema constraints**  
- Use JSON schemas for task specification to decouple from free-text prompts.  
- Require explicit `task_intent` field mapped from prompt by a dedicated interpreter.

**Human review**  
- Humans review robustness reports rather than single-output quality, adjusting templates and interpreters.  

### 13.7 Conversion to System Assets  

**Validator ideas**  
- `PromptRobustnessValidator`.  
- `OutputVarianceValidator` across prompt paraphrases.

**Enforcement rules**  
- `RULE_PROMPT_PARAPHRASE_STABILITY_MIN`: `agreement_rate >= τ`.  

**Benchmark fixtures**  
- Standardized paraphrase sets for key tasks; outputs evaluated for consistency. [arxiv](https://arxiv.org/abs/2602.06176)
- Regression suites that track changes across model versions and prompt tweaks.

**Library mapping:**  
- failure_mode_library: `prompt_sensitivity_failure`  
- evaluation_library: `robustness_metric`  


***

## 14. Formatting and Structure Drift

### 14.1 Definition  
Over long outputs, formats (lists, sections, headings) and structural conventions drift away from specified templates or schemas.

**Libraries:** failure_mode_library, continuity_state_library, evaluation_library  

### 14.2 Failure Mechanics  
- Models treat structure as stylistic suggestion, not as hard constraint, especially past early tokens.  
- Token-level decoding has no direct representation of document tree structure; headings and lists are just tokens.  
- Longer generation increases probability of unclosed or malformed structures.

### 14.3 Why Common Fixes Fail  
- Repeated instructions (“follow this format”) lose influence mid-document.  
- Post-hoc reformatting prompts must parse and rewrite large spans, often introducing new errors.  
- Using Markdown or HTML syntactic hints does not guarantee semantic adherence.

### 14.4 Detection Signals  
- Missing or malformed headings; list bullets turning into paragraphs or vice versa.  
- Inconsistent section ordering relative to template.  
- Schema violations when attempting to parse output into structured representations.

### 14.5 System Implications  
- Difficult to integrate outputs into downstream pipelines that assume structural consistency.  
- Human editors must manually reformat, negating automation gains.

### 14.6 Handling Strategies  

**Runtime logic**  
- Drive generation from structured templates (JSON or AST) and map to text, rather than free-form text first.  
- Incrementally parse partial outputs and validate structure; halt or correct when drift is detected.

**Enforcement rules**  
- “All required sections must be present exactly once and in specified order.”  
- “List items must adhere to bullet or numbering scheme defined in schema.”

**Validation systems**  
- Structural validators using schema validation (JSON Schema, XML Schema) on intermediate representations.  
- Markdown/HTML parsers that check for structural correctness and completeness.

**Schema constraints**  
- Mandatory explicit template objects (e.g., `sections[]`, `subsections[]`, `list_blocks[]`).  
- Require `format_version` and `schema_id` for each document.

**Human review**  
- Humans review structure via schema visualizers, not raw text; they correct template-level issues.

### 14.7 Conversion to System Assets  

**Validator ideas**  
- `StructureSchemaValidator`.  
- `MarkdownFormatValidator`.

**Enforcement rules**  
- `RULE_SECTION_PRESENCE`.  
- `RULE_LIST_FORMAT_INTEGRITY`.  

**Benchmark fixtures**  
- Documents intentionally perturbed to break structure; validators must detect and localize errors.  
- End-to-end tests with downstream parsers consuming generated documents.

**Library mapping:**  
- failure_mode_library: `structure_drift_failure`  
- continuity_state_library: `document_structure_state`  
- evaluation_library: `schema_conformity_metric`  


***

## 15. Weak Claim Architecture (Claim–Evidence–Warrant)

### 15.1 Definition  
Arguments contain claims and sometimes evidence but lack robust, explicit or implicit warrants connecting them, producing shallow or unpersuasive reasoning. [arxiv](https://arxiv.org/html/2601.17377v1)

**Libraries:** failure_mode_library, abstraction_control_library, evaluation_library  

### 15.2 Failure Mechanics  
- LLMs excel at generating plausible claims and evidence snippets but struggle to model the implicit common-sense warrants that justify inference. [arxiv](https://arxiv.org/html/2601.17377v1)
- Reasoning failures stem from shallow pattern matching rather than causal-world modeling. [emergentmind](https://www.emergentmind.com/topics/large-language-model-reasoning-failures)
- Training data often omits explicit argument structure annotations.

### 15.3 Why Common Fixes Fail  
- “Be more rigorous” prompts encourage more citations or restated evidence, not better warrants.  
- Chain-of-thought prompting improves narrative explanation but not warrant correctness. [arxiv](https://arxiv.org/abs/2602.06176)
- LLM-as-judge evaluation may accept superficially plausible but logically weak warrants. [arxiv](https://arxiv.org/html/2601.17377v1)

### 15.4 Detection Signals  
- Claims restate evidence in different words without adding inferential step.  
- Warrants rely on over-generalized or unstated assumptions that don’t hold under scrutiny.  
- NLI-based checks show weak entailment between evidence and claims given warrant. [arxiv](https://arxiv.org/html/2601.17377v1)

### 15.5 System Implications  
- Content appears reasoned but collapses under expert inspection.  
- Downstream factuality and trustworthiness metrics are inflated relative to actual argumentative strength. [arxiv](https://arxiv.org/html/2602.21045v1)

### 15.6 Handling Strategies  

**Runtime logic**  
- Explicitly model arguments as triples: claim, evidence, warrant; generate each under constraints. [arxiv](https://arxiv.org/html/2601.17377v1)
- Enforce warrant plausibility using separate reasoning models trained on warrant acceptability datasets. [arxiv](https://arxiv.org/html/2601.17377v1)

**Enforcement rules**  
- “Every non-trivial claim must be backed by at least one evidence span and one acceptable warrant.”  
- “Warrants must not contradict known facts or domain constraints.”

**Validation systems**  
- Use dedicated warrant evaluation models (e.g., WarrantScore-like) to score warrant acceptability and filter low scores. [arxiv](https://arxiv.org/html/2601.17377v1)
- Claim–evidence matching systems (e.g., PaperTrail-like) to ensure grounding and coverage. [arxiv](https://arxiv.org/html/2602.21045v1)

**Schema constraints**  
- Argument schemas with `claim_span`, `evidence_spans[]`, `warrant_span`, `warrant_score`.  
- Document-level `argument_graph` capturing relations among claims.

**Human review**  
- Experts review only contested warrants surfaced by low-scoring validators, not all text.  

### 15.7 Conversion to System Assets  

**Validator ideas**  
- `ClaimEvidenceLinkValidator`.  
- `WarrantAcceptabilityValidator` trained on warrant datasets. [arxiv](https://arxiv.org/html/2601.17377v1)

**Enforcement rules**  
- `RULE_CLAIM_SUPPORT_REQUIRED`.  
- `RULE_WARRANT_SCORE_MIN`: `warrant_score >= φ`.  

**Benchmark fixtures**  
- Corpora with annotated claims, evidence, and warrants; systems must reconstruct structures and meet acceptability thresholds. [arxiv](https://arxiv.org/html/2602.21045v1)
- Stress tests where evidence is strong but warrants are intentionally flawed; validators must detect.

**Library mapping:**  
- failure_mode_library: `weak_claim_architecture_failure`  
- abstraction_control_library: `argument_graph_store`  
- evaluation_library: `warrant_score_metric`, `argument_quality_metric`  


***

## RULESET_EXTRACT
- RULE_PROSE_CONCRETENESS_MIN
- RULE_GENERIC_TEMPLATE_CAP
- RULE_SPEAKER_STYLE_DISTANCE_MIN
- RULE_DIALOGUE_ACT_DIVERSITY_MIN
- RULE_SENTENCE_LENGTH_VAR_MIN
- RULE_SYNTAX_TEMPLATE_REPEAT_CAP
- RULE_SCENE_GOAL_REQUIRED
- RULE_PROMISE_RESOLUTION_RATE
- RULE_ENTITY_INVARIANT_ENFORCED
- RULE_CONTINUITY_CONTRADICTION_CAP
- RULE_ABSTRACTION_RATIO_MAX
- RULE_META_SENTENCE_RUN_CAP
- RULE_SEMANTIC_REDUNDANCY_CAP
- RULE_SECTION_NOVELTY_MIN
- RULE_AFFECT_VARIANCE_MIN
- RULE_GENERIC_EMOTION_CAP
- RULE_CANON_NO_IMPLICIT_OVERRIDE
- RULE_TERM_DEFINITION_STABILITY
- RULE_STYLE_DISTANCE_MAX
- RULE_CORPUS_STYLE_DIVERSITY_MIN
- RULE_VOICE_DRIFT_CAP
- RULE_REVISION_SCOPE_STYLE_LOCK
- RULE_GENRE_BEAT_COVERAGE_MIN
- RULE_GENRE_SIGNATURE_FEATURES_MIN
- RULE_PROMPT_PARAPHRASE_STABILITY_MIN
- RULE_SECTION_PRESENCE
- RULE_LIST_FORMAT_INTEGRITY
- RULE_CLAIM_SUPPORT_REQUIRED
- RULE_WARRANT_SCORE_MIN

## OPERATOR_EXTRACT
- OP-1: ProseConcretenessValidator
- OP-2: HumanLikenessDiscriminator
- OP-3: SpeakerDivergenceValidator
- OP-4: PragmaticsCoverageValidator
- OP-5: CadenceDistributionValidator
- OP-6: SyntaxTemplateRepetitionValidator
- OP-7: NarrativeGoalProgressValidator
- OP-8: PromisePayoffValidator
- OP-9: ContinuityNLIValidator
- OP-10: EntityAttributeDriftValidator
- OP-11: AbstractionDensityValidator
- OP-12: MetaExplanationPatternValidator
- OP-13: SemanticRedundancyValidator
- OP-14: DiscourseNoveltyValidator
- OP-15: AffectVarianceValidator
- OP-16: GenericEmotionPhraseValidator
- OP-17: WorldCanonConsistencyValidator
- OP-18: TermUsageConsistencyValidator
- OP-19: AuthorStyleFingerprintValidator
- OP-20: CorpusStyleDiversityValidator
- OP-21: StyleDriftValidator
- OP-22: VoiceInvariantPreservationValidator
- OP-23: GenreConformityValidator
- OP-24: GenreBeatCoverageValidator
- OP-25: PromptRobustnessValidator
- OP-26: OutputVarianceValidator
- OP-27: StructureSchemaValidator
- OP-28: MarkdownFormatValidator
- OP-29: ClaimEvidenceLinkValidator
- OP-30: WarrantAcceptabilityValidator

## FAILURE_MODE_EXTRACT
- FM-1: prose_naturalness_collapse
- FM-2: dialogue_realism_collapse
- FM-3: cadence_flattening_failure
- FM-4: narrative_drift_failure
- FM-5: long_form_coherence_failure
- FM-6: over_abstraction_failure
- FM-7: semantic_redundancy_failure
- FM-8: emotional_flattening_failure
- FM-9: continuity_memory_failure
- FM-10: style_homogenization_failure
- FM-11: voice_erosion_failure
- FM-12: genre_flattening_failure
- FM-13: prompt_sensitivity_failure
- FM-14: structure_drift_failure
- FM-15: weak_claim_architecture_failure

## TEST_CASE_EXTRACT
- TC-1: Human vs LLM prose naturalness ranking tasks using parallel prompts with concreteness and texture discriminators.
- TC-2: Multi-speaker scenes with permuted speaker identities to detect dialogue homogenization.
- TC-3: Cadence-only classification tasks distinguishing human vs LLM paragraphs using structural features.
- TC-4: Long narratives with removed climaxes to test narrative progression and payoff detection.
- TC-5: Documents with injected contradictions to test continuity and canon enforcement.
- TC-6: Argument corpora with annotated claims, evidence, and warrants to evaluate reasoning structure.
- TC-7: Prompt paraphrase robustness suites measuring output stability across equivalent prompts.
- TC-8: Genre corpora with beat annotations to detect genre conformity and flattening.
- TC-9: Revision workflows comparing human drafts vs LLM revisions to detect voice erosion.
- TC-10: Structured documents with formatting perturbations to test schema adherence.

## LIBRARY_EXTRACT
- failure_mode_library:
  - prose_naturalness_collapse
  - dialogue_realism_collapse
  - cadence_flattening_failure
  - narrative_drift_failure
  - long_form_coherence_failure
  - over_abstraction_failure
  - semantic_redundancy_failure
  - emotional_flattening_failure
  - continuity_memory_failure
  - style_homogenization_failure
  - voice_erosion_failure
  - genre_flattening_failure
  - prompt_sensitivity_failure
  - structure_drift_failure
  - weak_claim_architecture_failure

- abstraction_control_library:
  - concreteness_ratio_monitor
  - abstraction_level_tracker
  - proposition_graph_tracker
  - affect_curve_model
  - author_style_profile_store
  - genre_schema_store
  - argument_graph_store
  - tension_curve_model
  - voice_anchor_store

- dialogue_behavior_library:
  - speaker_state_embedding
  - dialogue_act_tracker

- cadence_library:
  - local_surprisal_var_tracker
  - sentence_length_monitor
  - syntax_template_tracker
  - author_cadence_profile

- continuity_state_library:
  - character_voice_state
  - narrative_goal_state
  - promise_registry
  - entity_registry
  - fact_invariant_store
  - world_canon_store
  - timeline_registry
  - document_structure_state
  - genre_beat_state

- evaluation_library:
  - human_likeness_disc
  - texture_score_metric
  - dialogue_realism_disc
  - cadence_realism_disc
  - arc_coherence_metric
  - coherence_over_distance_metric
  - abstraction_balance_metric
  - semantic_density_metric
  - affect_dynamics_metric
  - continuity_integrity_metric
  - style_fingerprint_metric
  - style_drift_metric
  - genre_conformity_metric
  - robustness_metric
  - schema_conformity_metric
  - warrant_score_metric
  - argument_quality_metric


Which of these failure modes do you want to prototype validators for first?  

For each failure mode, note whether solving it likely requires explicit state tracking, runtime enforcement, symbolic constraints, or purely statistical generation changes.