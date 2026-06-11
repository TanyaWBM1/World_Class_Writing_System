## 1. System Overview

This document specifies evaluation methods for “human-like” long-form narrative and dialogue, with emphasis on determinism, cross-run stability, and systematized failure-mode capture. [wandb](https://wandb.ai/onlineinference/genai-research/reports/Exploring-LLM-evaluations-and-benchmarking--VmlldzoxMzk0OTI0OA)

Each method is described in terms of mechanics, strengths, weaknesses, failure modes, determinism, and implementation targets (validator, scoring system, benchmark fixture, regression test), and is mapped to the specified libraries. [tredence](https://www.tredence.com/blog/llm-evaluation)


## 2. Human vs AI Writing Discrimination

### 2.1 Adversarial Discriminator (Reference-Free)

1. Description  
Discriminative model trained to classify passages as human vs model‑generated, used as a proxy for human-likeness in style and discourse. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)

2. How it works  
- Train a classifier (e.g., RoBERTa/BERT-style encoder) on labeled human vs AI corpora stratified by genre, length, and dialogue ratio. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)
- Optionally adversarially train with current target model generations to reduce overfitting to older model signatures. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)
- At evaluation, score passages; outputs: probability of “human,” calibration metrics, and per-span attributions (e.g., token-level scores). [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)

3. Strengths  
- Captures global stylistic and discourse cues without references. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)
- Can be run deterministically for fixed model weights and inference configuration. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)

4. Weaknesses  
- Susceptible to distribution shift; new model families may evade detectors trained on old generations. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)
- Encourages adversarial “detector gaming” rather than genuine narrative quality. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)

5. Failure modes  
- Misclassifies highly formulaic human text as AI, especially low-quality web writing. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)
- Overfits to superficial artifacts (punctuation, tokenization quirks) and misses deeper discourse incoherence. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)

6. Deterministic vs probabilistic  
- Fully deterministic given fixed model, precision, and no sampling; probabilistic only in a Bayesian or MC-dropout variant.  

7. System implementation options  
- Validator: hard threshold on human-probability for acceptance; flag low-human-like outputs.  
- Scoring system: continuous human-likeness score aggregated per story or per chapter.  
- Benchmark fixture: curated mixed human/model set, report ROC/AUC for discrimination.  
- Regression test: ensure discriminator score for new model stays within tolerance band vs prior version on fixed corpus.  

8. Library mapping  
- evaluation_library: `discriminator_human_like_v1`  
- benchmark_fixture_library: `mixed_human_ai_corpus_v1`  
- failure_mode_library: `detector_overfit_artifact_v1`  
- voice_library: `style_signature_features_v1`  
- cadence_library: `sentence_rhythm_profile_v1`  


### 2.2 LLM-as-Judge Human-Likeness Ranking

1. Description  
Use a strong language model as a comparative judge to rank or rate passages by perceived human-likeness, often via pairwise battles or rubric-anchored Likert scales. [aclanthology](https://aclanthology.org/2024.findings-emnlp.559.pdf)

2. How it works  
- Prompt LLM-judge with rubric describing human-like writing (naturalness, coherence, nuanced emotion, non-template phrasing). [web.stanford](https://web.stanford.edu/class/cs329x/slides/Lecture8_evaluate_HAI.pdf)
- Use pairwise comparison between candidate and a human reference or between two models; derive Elo or Bradley–Terry scores. [wandb](https://wandb.ai/onlineinference/genai-research/reports/Exploring-LLM-evaluations-and-benchmarking--VmlldzoxMzk0OTI0OA)
- Apply prompt stability controls (rubric locking, evidence quoting requirements). [aclanthology](https://aclanthology.org/2024.findings-emnlp.108.pdf)

3. Strengths  
- High alignment with human relative judgments when prompt and calibration are tuned. [emergentmind](https://www.emergentmind.com/topics/prompt-stability-scoring)
- Flexible across narrative, dialogue, and mixed formats; no need for token-level alignment. [aclanthology](https://aclanthology.org/2024.findings-emnlp.559.pdf)

4. Weaknesses  
- Sensitive to prompt wording and ordering of candidates, producing evaluation instability. [arxiv](https://arxiv.org/html/2603.15840v1)
- Judge model may share biases with system under test, masking failure modes. [aclanthology](https://aclanthology.org/2024.findings-emnlp.108.pdf)

5. Failure modes  
- Self-preference: family of judge model favors its own generations. [wandb](https://wandb.ai/onlineinference/genai-research/reports/Exploring-LLM-evaluations-and-benchmarking--VmlldzoxMzk0OTI0OA)
- Prompt drift: minor textual prompt edits induce large rank reversals. [arxiv](https://arxiv.org/html/2603.15840v1)

6. Deterministic vs probabilistic  
- Deterministic if judge is run with greedy decoding and fixed context; probabilistic if sampling or non-deterministic hardware paths are used. [tredence](https://www.tredence.com/blog/llm-evaluation)

7. System implementation options  
- Validator: reject outputs that lose against a human baseline or a minimum-quality reference in pairwise tests.  
- Scoring system: maintain Elo-style human-likeness scores per model and configuration.  
- Benchmark fixture: standardized pairwise battle pool across stories and dialogues.  
- Regression test: assert monotonic or non-regressive Elo score across model versions.  

8. Library mapping  
- evaluation_library: `llm_judge_human_like_pairwise_v2`  
- benchmark_fixture_library: `pairwise_human_reference_pool_v1`  
- failure_mode_library: `llm_judge_prompt_sensitivity_v1`  
- voice_library: `human_like_style_descriptors_v1`  
- cadence_library: `dialogue_turn_flow_metrics_v1`  


## 3. Rubric-Based Evaluation Systems

### 3.1 Human Rubric Annotation for Narrative and Dialogue

1. Description  
Structured human evaluation using Likert or continuous scales across defined dimensions such as coherence, engagement, naturalness, and context maintenance. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)

2. How it works  
- Design rubrics with clear criteria and anchors for story coherence, character consistency, dialogue naturalness, and emotional realism. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- Collect multiple independent ratings per sample, normalize per-rater (z-scores) to reduce bias, and aggregate to overall scores. [web.stanford](https://web.stanford.edu/class/cs329x/slides/Lecture8_evaluate_HAI.pdf)
- Apply standard statistical significance tests and inter-rater agreement measures (e.g., Krippendorff’s alpha). [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)

3. Strengths  
- High validity when raters see full dialogue history or full story context. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- Interpretable dimensions useful for directing model and prompt changes. [web.stanford](https://web.stanford.edu/class/cs329x/slides/Lecture8_evaluate_HAI.pdf)

4. Weaknesses  
- Expensive and slow; limited throughput and coverage. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- Subject to rater drift, anchoring, and context effects; requires careful rater training. [web.stanford](https://web.stanford.edu/class/cs329x/slides/Lecture8_evaluate_HAI.pdf)

5. Failure modes  
- Instability with small rater pools; large variance across runs. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- Misalignment between rubric wording and actual narrative goals, leading to misleading optimization. [web.stanford](https://web.stanford.edu/class/cs329x/slides/Lecture8_evaluate_HAI.pdf)

6. Deterministic vs probabilistic  
- Fundamentally probabilistic due to human variability; deterministic only at the aggregation function level for fixed ratings.  

7. System implementation options  
- Validator: use human rubric as gold standard to calibrate automated validators; not online.  
- Scoring system: provide ground-truth labels for training surrogate evaluators.  
- Benchmark fixture: held-out human-rated corpus for periodic re-evaluation.  
- Regression test: ensure automated evaluators stay correlated with human ratings over time.  

8. Library mapping  
- evaluation_library: `human_rubric_longform_v1`  
- benchmark_fixture_library: `human_rated_story_dialogue_set_v1`  
- failure_mode_library: `human_label_instability_v1`  
- voice_library: `rubric_voice_fidelity_dimension_v1`  
- cadence_library: `rubric_dialogue_naturalness_dimension_v1`  


### 3.2 LLM Rubric Scoring (Structured Prompts)

1. Description  
Use LLMs guided by explicit rubrics to output scores and justifications for narrative dimensions such as coherence, continuity, and style consistency. [emergentmind](https://www.emergentmind.com/topics/prompt-stability-scoring)

2. How it works  
- Provide rubric definitions and explicit scoring instructions (e.g., 1–5 scale with labeled anchors) in the prompt. [aclanthology](https://aclanthology.org/2024.findings-emnlp.559.pdf)
- Force the model to quote evidence spans from the text and compute scores via a constrained format to reduce hallucinated judgments. [emergentmind](https://www.emergentmind.com/topics/prompt-stability-scoring)
- Apply prompt stability procedures (multiple paraphrased rubric prompts, aggregate scores). [aclanthology](https://aclanthology.org/2024.findings-emnlp.108.pdf)

3. Strengths  
- Scalable, cost-efficient, and able to cover many samples and model variants. [tredence](https://www.tredence.com/blog/llm-evaluation)
- Interpretability via textual rationales and evidence spans.  

4. Weaknesses  
- Sensitive to rubric wording and order effects; can be prompt-gamed. [aclanthology](https://aclanthology.org/2024.findings-emnlp.108.pdf)
- Judge model biases can reduce correlation with human preferences or narrative domain specifics. [wandb](https://wandb.ai/onlineinference/genai-research/reports/Exploring-LLM-evaluations-and-benchmarking--VmlldzoxMzk0OTI0OA)

5. Failure modes  
- Mode-collapse in scoring (most outputs get mid-range scores); poor discrimination. [tredence](https://www.tredence.com/blog/llm-evaluation)
- Self-consistency bias: same family of models both generates and evaluates, concealing shared weaknesses. [aclanthology](https://aclanthology.org/2024.findings-emnlp.559.pdf)

6. Deterministic vs probabilistic  
- Can be run deterministically with greedy decoding and fixed prompt; residual variance from non-deterministic system implementations needs control.  

7. System implementation options  
- Validator: thresholds on rubric dimensions (e.g., minimum coherence and continuity scores).  
- Scoring system: continuous metrics for optimization and comparison across experiments.  
- Benchmark fixture: fixed prompt templates and story pools; periodic re-scoring and trend tracking.  
- Regression test: assert no regression in rubric scores for representative suites of stories and dialogues.  

8. Library mapping  
- evaluation_library: `llm_rubric_scorer_v2`  
- benchmark_fixture_library: `rubric_story_dialogue_suite_v1`  
- failure_mode_library: `rubric_prompt_drift_v1`  
- voice_library: `rubric_style_consistency_dimension_v1`  
- cadence_library: `rubric_turn_cadence_dimension_v1`  


## 4. Narrative Coherence and Continuity

### 4.1 Structured Narrative Coherence Benchmarks

1. Description  
Benchmarks that require satisfying multiple story constraints and maintaining plot and character consistency across long contexts. [arxiv](https://arxiv.org/html/2503.23512v1)

2. How it works  
- Define tasks requiring integration of mandated elements (characters, objects, motivations, locations) and specific continuity constraints. [github](https://github.com/lechmazur/writing)
- Automatically or semi-automatically score element satisfaction, contradiction detection, and recall of earlier details. [arxiv](https://arxiv.org/html/2503.23512v1)
- Use composite metrics: element coverage, contradiction rate, temporal consistency, and emotional progression. [arxiv](https://arxiv.org/html/2503.23512v1)

3. Strengths  
- Directly targets long-range coherence and memory, not just local fluency. [github](https://github.com/lechmazur/writing)
- Amenable to deterministic scoring via symbolic checks and extraction models. [github](https://github.com/lechmazur/writing)

4. Weaknesses  
- Over-focus on explicit elements; subtle thematic coherence may be under-measured. [arxiv](https://arxiv.org/html/2503.23512v1)
- Template-like constraints risk encouraging checklist fulfillment instead of organic storytelling. [github](https://github.com/lechmazur/writing)

5. Failure modes  
- Models learn to game element inclusion while violating deeper narrative logic. [arxiv](https://arxiv.org/html/2503.23512v1)
- Automatic checkers mis-extract entities in complex or experimental prose.  

6. Deterministic vs probabilistic  
- Deterministic if extraction and rule logic are deterministic; probabilistic only if using stochastic extraction models.  

7. System implementation options  
- Validator: enforce minimum constraint satisfaction and contradiction-avoidance scores for release candidates.  
- Scoring system: track composite coherence indexes across model versions.  
- Benchmark fixture: dedicated long-form narrative benchmark (e.g., multi-episode stories).  
- Regression test: fixed seed stories re-generated with identical prompts to test consistency of constraint satisfaction.  

8. Library mapping  
- evaluation_library: `narrative_coherence_metric_v2`  
- benchmark_fixture_library: `multi_constraint_story_benchmark_v1`  
- failure_mode_library: `checklist_story_gaming_v1`  
- voice_library: `character_voice_persistence_features_v1`  
- cadence_library: `episode_transition_cadence_v1`  


### 4.2 State-Tracking and Continuity Checkers

1. Description  
Systems that track entities, attributes, and events over time to detect contradictions and continuity breaks in stories. [arxiv](https://arxiv.org/html/2503.23512v1)

2. How it works  
- Maintain symbolic or graph-based state of characters, objects, locations, and relationships. [arxiv](https://arxiv.org/html/2503.23512v1)
- At each narrative segment, update state via information extraction and check for inconsistencies (e.g., color changes, “dead but speaking”). [arxiv](https://arxiv.org/html/2503.23512v1)
- Use RAG-style retrieval of earlier episodes plus logical rules to validate current segment. [arxiv](https://arxiv.org/html/2503.23512v1)

3. Strengths  
- High sensitivity to concrete continuity errors and explicit contradictions. [arxiv](https://arxiv.org/html/2503.23512v1)
- Explainable: can point to specific earlier sentences that conflict with current text.  

4. Weaknesses  
- Limited coverage of implicit or psychological continuity (motives, subtle emotional arcs). [arxiv](https://arxiv.org/html/2503.23512v1)
- Extraction errors propagate and can generate false positives or false negatives.  

5. Failure modes  
- Over-penalizing creative or intentionally unreliable narration that violates naive assumptions. [arxiv](https://arxiv.org/html/2503.23512v1)
- Missing cross-document continuity issues when context windowing is misconfigured.  

6. Deterministic vs probabilistic  
- Deterministic rule engine with deterministic extraction models; probabilistic if extraction uses sampling or ambiguous resolutions.  

7. System implementation options  
- Validator: gate outputs that introduce hard contradictions relative to established state.  
- Scoring system: per-episode continuity score and global contradiction count.  
- Benchmark fixture: synthetic and real story sets with seeded continuity errors.  
- Regression test: ensure continuity detection sensitivity does not regress when updating extraction models.  

8. Library mapping  
- evaluation_library: `story_state_consistency_checker_v1`  
- benchmark_fixture_library: `seeded_continuity_error_corpus_v1`  
- failure_mode_library: `extraction_cascade_failure_v1`  
- voice_library: `character_state_emotional_profile_v1`  
- cadence_library: `event_progression_cadence_v1`  


## 5. Dialogue Realism Evaluation

### 5.1 Human Live Conversation Evaluation

1. Description  
Humans converse live with dialogue agents and rate the conversations along realism, naturalness, and engagement dimensions. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)

2. How it works  
- Human assessors engage in multi-turn conversations with models under standardized instructions and persona conditions. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- After sessions, raters score attributes (e.g., understandable, natural, maintains context, interesting, uses knowledge, overall quality). [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- Scores are normalized per worker to account for individual rating scales. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)

3. Strengths  
- High ecological validity; raters experience full dialogue history and topic dynamics. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)
- Captures subtle cues such as timing of responses and turn-taking behaviors conceptually.  

4. Weaknesses  
- Expensive and time-consuming; limited sample sizes. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)
- Hard to control topic variability and user-driven branching; noisy metrics. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)

5. Failure modes  
- Ratings confounded by conversation topic difficulty rather than model quality. [aclanthology](https://aclanthology.org/2022.acl-long.445.pdf)
- Persona or prompt variations overshadow underlying model differences.  

6. Deterministic vs probabilistic  
- Essentially probabilistic due to human and interaction stochasticity; deterministic aggregation only.  

7. System implementation options  
- Validator: not inline; used to calibrate automatic dialogue realism metrics.  
- Scoring system: global quality benchmarks for target personas and scenarios.  
- Benchmark fixture: standardized human evaluation rounds for major releases.  
- Regression test: correlation stability between automatic metrics and human scores.  

8. Library mapping  
- evaluation_library: `human_dialogue_realism_rubric_v1`  
- benchmark_fixture_library: `live_conversation_sessions_v1`  
- failure_mode_library: `topic_confounding_v1`  
- voice_library: `persona_adherence_dimension_v1`  
- cadence_library: `turn_level_context_maintenance_v1`  


### 5.2 Automated Dialogue Metrics (Reference-Free / Hybrid)

1. Description  
Automatic metrics that assess dialogue responses via semantic similarity, informativeness, coherence, and human-likeness using embeddings and trained evaluators. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)

2. How it works  
- Compute reference-based metrics when ground truth replies exist, or reference-free metrics like adversarial discriminators, RUBER-style hybrid scores, and learned evaluators (USR, RoBERTa-eval).! [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)
- Aggregate per-turn metrics into conversation-level scores (average and tail behavior).! [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)

3. Strengths  
- Efficient and scalable across large corpora. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)
- Can be tailored to emphasize continuity and non-repetitiveness in multi-turn dialogues.! [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)

4. Weaknesses  
- Only moderately correlated with human judgments, especially for open-domain chitchat. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)
- Sensitive to reference quality and domain mismatch. [ar5iv.labs.arxiv](https://ar5iv.labs.arxiv.org/html/2108.01369)

5. Failure modes  
- Reward surface-level similarity and penalize creative or diversified replies. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC7817575/)
- Over-penalize benign repetition in certain narrative styles while missing deeper incoherence.  

6. Deterministic vs probabilistic  
- Deterministic embedding and scoring functions; probabilistic only if evaluators use sampled inference.  

7. System implementation options  
- Validator: minimum dialogue coherence and non-repetitiveness scores per conversation.  
- Scoring system: continuous conversation-level realism score for optimization.  
- Benchmark fixture: curated multi-turn test dialogs with human annotations for calibration.  
- Regression test: maintain or improve correlation with human evaluations across model updates.  

8. Library mapping  
- evaluation_library: `dialogue_automatic_metric_suite_v2`  
- benchmark_fixture_library: `multi_turn_reference_dialogue_set_v1`  
- failure_mode_library: `semantic_similarity_overweight_v1`  
- voice_library: `dialogue_style_signature_v1`  
- cadence_library: `turn_repetition_profile_v1`  


## 6. Style Consistency, Voice, and Cadence

### 6.1 Style Consistency and Drift Detection

1. Description  
Measure whether a model preserves a defined stylistic voice and cadence across long outputs and across model versions.  

2. How it works  
- Train or define style embeddings from human reference corpora representing target voice and cadence (syntax, rhythm, lexical choices). [reddit](https://www.reddit.com/r/singularity/comments/1hv3bdn/new_llm_creative_storywriting_benchmark_claude_35/)
- Compute distance between generated text and reference style embeddings over segments; track variance and drift across chapters and time. [reddit](https://www.reddit.com/r/singularity/comments/1hv3bdn/new_llm_creative_storywriting_benchmark_claude_35/)
- Use change-point detection to identify points where style shifts beyond tolerance.  

3. Strengths  
- Supports enforcing **voice** preservation for branded characters or authors. [reddit](https://www.reddit.com/r/singularity/comments/1hv3bdn/new_llm_creative_storywriting_benchmark_claude_35/)
- Quantifies style drift both within a single work and across releases.  

4. Weaknesses  
- Style embeddings may entangle topic and voice; domain shift can be misinterpreted as style drift. [reddit](https://www.reddit.com/r/singularity/comments/1hv3bdn/new_llm_creative_storywriting_benchmark_claude_35/)
- Hard to capture nuanced authorial choices like irony or subtext.  

5. Failure modes  
- False positives when narrative intentionally changes style between acts or POVs.  
- False negatives when voice erosion is subtle but semantically significant.  

6. Deterministic vs probabilistic  
- Deterministic given fixed embedding model and pipeline.  

7. System implementation options  
- Validator: enforce maximum style distance from reference within each unit (chapter, episode).  
- Scoring system: style stability index per story and per model.  
- Benchmark fixture: suites of stories with labeled target voices and style transitions.  
- Regression test: style distance trends across model versions and experiments.  

8. Library mapping  
- evaluation_library: `style_consistency_metric_v2`  
- benchmark_fixture_library: `voice_locked_story_suite_v1`  
- failure_mode_library: `false_positive_style_shift_v1`  
- voice_library: `author_style_embedding_space_v1`  
- cadence_library: `prosodic_cadence_features_v1`  


### 6.2 Voice Preservation after Editing

1. Description  
Evaluate whether editing or post-processing operations preserve the original narrative voice while improving clarity or correctness.  

2. How it works  
- Extract style vectors for original and edited text via style encoder; compute similarity. [reddit](https://www.reddit.com/r/singularity/comments/1hv3bdn/new_llm_creative_storywriting_benchmark_claude_35/)
- Use LLM-judge with rubric “preserve voice, improve clarity” to rate voice preservation qualitatively. [emergentmind](https://www.emergentmind.com/topics/prompt-stability-scoring)
- Track semantic preservation via entailment/paraphrase models to ensure meaning has not drifted.  

3. Strengths  
- Separates editing quality from voice fidelity, enabling constrained editing systems.  
- Useful for deterministic editing pipelines where output should remain stylistically aligned.  

4. Weaknesses  
- Style encoder quality limits sensitivity to subtle shifts.  
- LLM-judge may prefer its own editing patterns, biasing scores.  

5. Failure modes  
- Over-penalizing legitimate voice changes when user intentionally requests tone shift.  
- Missing slow erosion where repeated small edits cumulatively alter voice.  

6. Deterministic vs probabilistic  
- Deterministic similarity pipeline; probabilistic only when LLM-as-judge is sampled.  

7. System implementation options  
- Validator: reject edits whose style similarity falls below threshold, given stable semantics.  
- Scoring system: voice preservation score per editing operation or pipeline version.  
- Benchmark fixture: hand-edited vs auto-edited pairs with human labels for voice preservation.  
- Regression test: ensure new editing models do not reduce voice preservation metrics.  

8. Library mapping  
- evaluation_library: `voice_preservation_after_edit_v1`  
- benchmark_fixture_library: `edited_pairs_voice_labelled_v1`  
- failure_mode_library: `cumulative_voice_erosion_v1`  
- voice_library: `pre_post_edit_style_encoder_v1`  
- cadence_library: `edit_preserved_cadence_delta_v1`  


## 7. Template Echo / Example Overfitting

### 7.1 Template Echo Detection

1. Description  
Detect when outputs closely mimic prompt templates, system examples, or training exemplars, indicating overfitting or pattern echo rather than original composition.  

2. How it works  
- Maintain embedding and n-gram signature library of templates and canonical examples used in system prompts or fine-tuning. [labs.lamatic](https://labs.lamatic.ai/p/llm-benchmarks/)
- Compute similarity between new outputs and stored signatures; flag high similarity spans.  
- Use LLM-judge to classify whether text reads as “template-like” or “overly generic” vs context.  

3. Strengths  
- Mitigates blind reuse of few-shot exemplars, improving narrative diversity.  
- Supports deterministic checks via fixed similarity thresholds.  

4. Weaknesses  
- Risk of penalizing legitimate stylistic homages or genre tropes.  
- Template library maintenance overhead.  

5. Failure modes  
- Failure to update template library when prompts change, reducing detection coverage.  
- Over-penalizing repeated structural patterns needed for certain formats (e.g., scripts).  

6. Deterministic vs probabilistic  
- Deterministic similarity search; probabilistic if LLM-judge classification is used.  

7. System implementation options  
- Validator: block outputs exceeding template similarity thresholds for protected contexts.  
- Scoring system: template echo index aggregated by model configuration.  
- Benchmark fixture: synthetic tasks constructed to provoke template echo; test detection.  
- Regression test: ensure template echo rate does not increase after retraining or prompt changes.  

8. Library mapping  
- evaluation_library: `template_echo_detector_v1`  
- benchmark_fixture_library: `template_echo_challenge_set_v1`  
- failure_mode_library: `genre_trope_false_positive_v1`  
- voice_library: `template_signature_voice_space_v1`  
- cadence_library: `template_rhythm_signature_v1`  


## 8. Evaluation Instability, Prompt Sensitivity, and Cross-Run Stability

### 8.1 Prompt Sensitivity Measurement

1. Description  
Quantify variation in evaluation scores and model outputs under small, semantics-preserving prompt perturbations. [arxiv](https://arxiv.org/pdf/2509.13680.pdf)

2. How it works  
- Generate sets of semantically equivalent prompt variants using controlled perturbations (emotion, politeness, wording templates). [arxiv](https://arxiv.org/pdf/2509.13680.pdf)
- Measure differences in outputs and scores (e.g., PromptSE-like probability-aware sensitivity or discrete agreement metrics) across variants. [arxiv](https://arxiv.org/pdf/2509.13680.pdf)
- Analyze sensitivity as a function of perturbation “distance” and prompt type. [arxiv](https://arxiv.org/html/2603.15840v1)

3. Strengths  
- Turns stability into a measurable construct rather than intuition. [arxiv](https://arxiv.org/pdf/2509.13680.pdf)
- Reveals brittle regimes where minor phrasing changes drastically affect behavior or evaluation.  

4. Weaknesses  
- Requires careful design of perturbation generators to preserve semantics. [arxiv](https://arxiv.org/pdf/2509.13680.pdf)
- Sensitive to evaluation noise; needs repeated measures for reliable estimates. [arxiv](https://arxiv.org/html/2603.15840v1)

5. Failure modes  
- Confounding actual semantic differences when perturbations inadvertently change task. [aclanthology](https://aclanthology.org/2024.findings-emnlp.108.pdf)
- Over-generalizing from narrow prompt families to all user prompts. [arxiv](https://arxiv.org/html/2603.15840v1)

6. Deterministic vs probabilistic  
- Deterministic when models and evaluators are run deterministically; sensitivity still measured as differences across prompts.  

7. System implementation options  
- Validator: require maximum allowed sensitivity score for critical prompts.  
- Scoring system: prompt stability score per model and config.  
- Benchmark fixture: curated prompt families with documented perturbation patterns.  
- Regression test: ensure prompt sensitivity does not degrade with new deployments.  

8. Library mapping  
- evaluation_library: `prompt_sensitivity_metric_v2`  
- benchmark_fixture_library: `prompt_variant_family_suite_v1`  
- failure_mode_library: `prompt_brittleness_cluster_v1`  
- voice_library: `prompt_style_invariance_features_v1`  
- cadence_library: `prompt phrasing_cadence_invariance_v1`  


### 8.2 Cross-Run Stability and Agreement

1. Description  
Measure the consistency of outputs and evaluation scores across repeated runs with identical inputs and configurations. [emergentmind](https://www.emergentmind.com/topics/prompt-stability-scoring)

2. How it works  
- For non-deterministic models, perform multiple runs per prompt; compute overlap metrics (e.g., Jaccard, overlap coefficient) and score variance. [arxiv](https://arxiv.org/html/2603.15840v1)
- For deterministic architectures, verify bit-wise identical outputs and stable evaluator scores under fixed seeds and hardware profile.  
- Analyze divergence between internal stability and alignment with external references. [arxiv](https://arxiv.org/html/2603.15840v1)

3. Strengths  
- Detects hidden stochastic failure modes and reveals when stable behavior masks incorrect reasoning. [arxiv](https://arxiv.org/pdf/2509.13680.pdf)
- Provides regression hooks for deterministic systems to guarantee reproducibility.  

4. Weaknesses  
- Excessive focus on stability can ignore correctness gaps. [arxiv](https://arxiv.org/html/2603.15840v1)
- For deterministic models, cross-run stability is trivial; requires coupling with reference agreement metrics.  

5. Failure modes  
- Mistaking high stability with high quality when outputs consistently fail tests. [arxiv](https://arxiv.org/html/2603.15840v1)
- Under-sampling leading to over- or under-estimation of instability in stochastic models.  

6. Deterministic vs probabilistic  
- Measurement procedure can be deterministic; underlying model may be probabilistic.  

7. System implementation options  
- Validator: assert run-to-run stability thresholds on evaluation pipelines.  
- Scoring system: stability indices per metric and per task.  
- Benchmark fixture: fixed corpus and configuration matrix to repeatedly test stability.  
- Regression test: ensure stability and quality metrics remain within expected envelope over time.  

8. Library mapping  
- evaluation_library: `cross_run_stability_metric_v1`  
- benchmark_fixture_library: `stability_reference_corpus_v1`  
- failure_mode_library: `stable_but_wrong_pattern_v1`  
- voice_library: `run_invariant_voice_features_v1`  
- cadence_library: `run_invariant_cadence_features_v1`  


## 9. Continuity, Memory, and Long-Range Dependencies

### 9.1 Memory and Recall Benchmarks

1. Description  
Benchmarks that evaluate capacity to recall and correctly use information introduced many tokens earlier in narratives or dialogues.  

2. How it works  
- Insert key facts, character traits, or world rules early in narrative; require correct usage or reference much later. [github](https://github.com/lechmazur/writing)
- Evaluate recall using extraction and matching, and penalize contradictions or hallucinated changes.  
- Design tasks with varying distance and interference to characterize memory decay curves.  

3. Strengths  
- Directly probes long-range dependency handling rather than local n-gram coherence.  
- Supports deterministic scoring via explicit ground-truth facts.  

4. Weaknesses  
- Synthetic tasks may not fully match real narrative complexity.  
- Over-emphasis on discrete facts, under-emphasis on soft continuity (tone, motifs).  

5. Failure modes  
- Models optimize for memorizing benchmark patterns rather than general memory.  
- Extraction failures when paraphrasing is highly creative.  

6. Deterministic vs probabilistic  
- Deterministic scoring pipeline; model may be deterministic or not.  

7. System implementation options  
- Validator: enforce minimum recall and non-contradiction scores for long stories.  
- Scoring system: memory retention curves across token distances and interference levels.  
- Benchmark fixture: layered memory tasks across narrative and dialogue formats.  
- Regression test: track memory metrics across architecture changes and context window adjustments.  

8. Library mapping  
- evaluation_library: `long_range_memory_benchmark_metric_v1`  
- benchmark_fixture_library: `multi_distance_memory_suite_v1`  
- failure_mode_library: `memory_interference_collapse_v1`  
- voice_library: `longitudinal_voice_persistence_v1`  
- cadence_library: `long_range_cadence_consistency_v1`  


## 10. System Implementation: Validator, Scoring, Benchmarks, Regression

### 10.1 Validator Roles

- Enforce hard constraints: no blatant continuity contradictions, minimum narrative coherence, maximum template echo and style drift, minimum voice preservation after edits. [reddit](https://www.reddit.com/r/singularity/comments/1hv3bdn/new_llm_creative_storywriting_benchmark_claude_35/)
- Run deterministically as part of CI/CD before outputs enter production or training corpora.  

### 10.2 Scoring System Roles

- Maintain continuous metrics over time: human-likeness, narrative coherence, dialogue realism, style consistency, stability, and prompt sensitivity. [labs.lamatic](https://labs.lamatic.ai/p/llm-benchmarks/)
- Support dashboards and automated alerts on metric regressions.  

### 10.3 Benchmark Fixture Roles

- Provide fixed corpora, prompt suites, and conversation scenarios for periodic evaluation across model versions. [labs.lamatic](https://labs.lamatic.ai/p/llm-benchmarks/)
- Include both synthetic stress tests and human-authored references.  

### 10.4 Regression Test Roles

- Run subsets of benchmarks with tight tolerances on stability and quality metrics in pre-deployment pipelines. [emergentmind](https://www.emergentmind.com/topics/prompt-stability-scoring)
- Validate both deterministic behavior and alignment with human-grounded targets.  


## RULESET_EXTRACT

- RULE-1: All core evaluation paths MUST be deterministic for fixed inputs and configuration in the deterministic writing architecture.  
- RULE-2: Human-like quality MUST be operationalized via multi-dimensional rubrics including coherence, continuity, dialogue realism, style consistency, and human-likeness discrimination.  
- RULE-3: Every validator MUST have documented thresholds and associated failure modes in failure_mode_library.  
- RULE-4: Prompt sensitivity and cross-run stability MUST be measured explicitly for all judge and scoring subsystems.  
- RULE-5: Template echo detection MUST run on any output produced under few-shot or example-based prompting regimes.  
- RULE-6: Voice preservation and style drift metrics MUST be applied before and after any automated editing or post-processing step.  
- RULE-7: Benchmarks MUST include long-form narrative and multi-turn dialogue fixtures with seeded continuity and memory challenges.  
- RULE-8: All evaluation components MUST map to entries in evaluation_library, benchmark_fixture_library, failure_mode_library, voice_library, and cadence_library.  


## OPERATOR_EXTRACT

- OP-1: Configure evaluators (LLM-judges, discriminators, metrics) to run with greedy decoding and fixed seeds to ensure deterministic behavior.  
- OP-2: For any change to prompts, rubrics, or fixtures, record a new version identifier and run prompt sensitivity and stability checks.  
- OP-3: Periodically re-calibrate automated evaluators against human rubric benchmarks for both narrative and dialogue.  
- OP-4: Monitor style consistency dashboards to detect unexpected voice drift across releases.  
- OP-5: Apply template echo detector to sample batches for each major prompt or fine-tune version, adjusting thresholds using benchmark fixtures.  
- OP-6: For editing pipelines, measure voice preservation and semantic fidelity before enabling new editors in production.  
- OP-7: Maintain and periodically expand benchmark_fixture_library with newly observed real-world failure examples.  
- OP-8: Use regression tests to block deployments where stability improves but agreement with human or reference metrics degrades.  


## FAILURE_MODE_EXTRACT

- FM-1: Detector overfit to superficial artifacts misclassifies human text as AI or vice versa.  
- FM-2: LLM-as-judge exhibits prompt sensitivity, self-preference, and rubric drift, masking true quality.  
- FM-3: Narrative coherence benchmarks are gamed via checklist inclusion, not genuine plot logic.  
- FM-4: State-tracking continuity checker cascades extraction errors and reports false contradictions.  
- FM-5: Dialogue metrics overweight semantic similarity, penalizing creative or diverse responses.  
- FM-6: Style drift detector flags intentional stylistic shifts (e.g., POV changes) as regressions.  
- FM-7: Template echo detector misclassifies genre-typical structures as template copies.  
- FM-8: Stability metrics report “stable but wrong” patterns where outputs are consistent yet misaligned with references or human judgment.  
- FM-9: Memory benchmarks encourage benchmark-specific pattern learning instead of general long-range reasoning.  
- FM-10: Editing pipelines slowly erode voice through cumulative small changes that evade single-step checks.  


## TEST_CASE_EXTRACT

- TC-1: Human vs AI discrimination – evaluate mixed corpus using discriminator_human_like_v1 and llm_judge_human_like_pairwise_v2; assert AUC and Elo within target ranges.  
- TC-2: Narrative coherence – run multi_constraint_story_benchmark_v1 with story_state_consistency_checker_v1; verify constraint satisfaction and low contradiction rate.  
- TC-3: Dialogue realism – evaluate multi_turn_reference_dialogue_set_v1 with dialogue_automatic_metric_suite_v2 and human_dialogue_realism_rubric_v1 alignment checks.  
- TC-4: Style consistency – compute style_consistency_metric_v2 over voice_locked_story_suite_v1 across chapters; assert drift within predefined thresholds.  
- TC-5: Voice preservation after editing – measure voice_preservation_after_edit_v1 and semantic fidelity on edited_pairs_voice_labelled_v1; compare to human labels.  
- TC-6: Template echo – run template_echo_detector_v1 on template_echo_challenge_set_v1; expect high recall of seeded template echoes with controlled false-positive rate.  
- TC-7: Prompt sensitivity – apply prompt_sensitivity_metric_v2 to prompt_variant_family_suite_v1 for all evaluators; ensure sensitivity scores below ceiling per task.  
- TC-8: Cross-run stability – compute cross_run_stability_metric_v1 on stability_reference_corpus_v1 under repeated runs; check both stability and correctness vs references.  
- TC-9: Memory – evaluate long_range_memory_benchmark_metric_v1 on multi_distance_memory_suite_v1; derive retention curves and detect interference-related collapses.  
- TC-10: Integrated pipeline – run full narrative generation, editing, and evaluation chain on mixed benchmark fixtures; ensure no critical validators fail and all scores meet release criteria.  


## LIBRARY_EXTRACT

- evaluation_library  
  - discriminator_human_like_v1  
  - llm_judge_human_like_pairwise_v2  
  - human_rubric_longform_v1  
  - llm_rubric_scorer_v2  
  - narrative_coherence_metric_v2  
  - story_state_consistency_checker_v1  
  - human_dialogue_realism_rubric_v1  
  - dialogue_automatic_metric_suite_v2  
  - style_consistency_metric_v2  
  - voice_preservation_after_edit_v1  
  - template_echo_detector_v1  
  - prompt_sensitivity_metric_v2  
  - cross_run_stability_metric_v1  
  - long_range_memory_benchmark_metric_v1  

- benchmark_fixture_library  
  - mixed_human_ai_corpus_v1  
  - pairwise_human_reference_pool_v1  
  - human_rated_story_dialogue_set_v1  
  - rubric_story_dialogue_suite_v1  
  - multi_constraint_story_benchmark_v1  
  - seeded_continuity_error_corpus_v1  
  - live_conversation_sessions_v1  
  - multi_turn_reference_dialogue_set_v1  
  - voice_locked_story_suite_v1  
  - edited_pairs_voice_labelled_v1  
  - template_echo_challenge_set_v1  
  - prompt_variant_family_suite_v1  
  - stability_reference_corpus_v1  
  - multi_distance_memory_suite_v1  

- failure_mode_library  
  - detector_overfit_artifact_v1  
  - llm_judge_prompt_sensitivity_v1  
  - human_label_instability_v1  
  - rubric_prompt_drift_v1  
  - checklist_story_gaming_v1  
  - extraction_cascade_failure_v1  
  - semantic_similarity_overweight_v1  
  - false_positive_style_shift_v1  
  - genre_trope_false_positive_v1  
  - stable_but_wrong_pattern_v1  
  - memory_interference_collapse_v1  
  - cumulative_voice_erosion_v1  

- voice_library  
  - style_signature_features_v1  
  - human_like_style_descriptors_v1  
  - rubric_voice_fidelity_dimension_v1  
  - character_voice_persistence_features_v1  
  - persona_adherence_dimension_v1  
  - dialogue_style_signature_v1  
  - author_style_embedding_space_v1  
  - pre_post_edit_style_encoder_v1  
  - template_signature_voice_space_v1  
  - prompt_style_invariance_features_v1  
  - longitudinal_voice_persistence_v1  
  - run_invariant_voice_features_v1  

- cadence_library  
  - sentence_rhythm_profile_v1  
  - dialogue_turn_flow_metrics_v1  
  - rubric_dialogue_naturalness_dimension_v1  
  - episode_transition_cadence_v1  
  - event_progression_cadence_v1  
  - turn_level_context_maintenance_v1  
  - turn_repetition_profile_v1  
  - prosodic_cadence_features_v1  
  - edit_preserved_cadence_delta_v1  
  - template_rhythm_signature_v1  
  - prompt_phrasing_cadence_invariance_v1  
  - long_range_cadence_consistency_v1  

Which dimension do you want specified first for concrete schema design: validators, benchmarks, or style/voice encoders?