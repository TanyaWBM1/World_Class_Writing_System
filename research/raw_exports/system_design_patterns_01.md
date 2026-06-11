## 0. System framing and libraries

Target architecture: deterministic orchestration around non-deterministic models, with strict schemas, replayable fixtures, and governed self-improvement loops. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)

### Library mapping

- **system_design_library**
  - Agent topology, pipelines, orchestration graphs, governance flows, versioning.
- **failure_mode_library**
  - Taxonomy of prose failures, detection rules, regression alerts, drift detectors. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)
- **benchmark_fixture_library**
  - Frozen prompts, expected behaviors, gold references, style snapshots, replay suites. [dev](https://dev.to/hybridtechie/ai-regression-tests-written-in-markdown-not-code-5b09)
- **evaluation_library**
  - Scoring functions, critics, rule-based checkers, hybrid evaluators, LLM-as-judge wrappers. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
- **continuity_state_library**
  - Long-form state, entity memory, narrative threads, style fingerprints, continuity contracts. [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)

All patterns below are expressed so they can be bound into these libraries.

***

## 1. Failure accumulation systems

### 1.1 Pattern: Structured Failure Ledger

1) **System design pattern**

- Central “failure ledger” that records every detected failure with a stable schema:
  - failure_id, fixture_id, agent_version, pipeline_stage, failure_type, features (embedding, style fingerprint, length, genre), evaluator_outputs, human_labels, and resolution_status. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)
- Ledger is append-only; resolution creates new rows (resolution events) instead of overwriting older failures.

2) **Why it works / fails**

- Works because:
  - You can differentiate systemic failures (many similar failures across fixtures) from one-offs (isolated cases). [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)
  - Provides material for self-improvement loops and new benchmarks.
- Fails if:
  - Failure taxonomy is too coarse (everything becomes “generic output”).
  - Evaluators are noisy, so many spurious “failures” accumulate and dilute signal. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)

3) **Implementation in subagent architecture**

- **Generation subagent**: emits structured outputs with trace ids.
- **Evaluation subagents**: style critic, coherence critic, factual critic, each produce standardized JSON verdicts.
- **Failure taxonomy subagent**:
  - Reads evaluation outputs and maps to normalized failure_types.
- **Failure logging subagent**:
  - Normalizes and writes to the failure ledger service.

4) **Required artifacts**

- `failure_log.jsonl` (append only):
  - Each line is a failure event.
- `failure_taxonomy.json`:
  - Controlled vocabulary of failure types and mapping rules.
- Aggregated reports:
  - `failure_summary_report.json` (grouped by version, pipeline stage, fixture).

5) **Risks and failure cases**

- Ledger becomes a dumping ground; no strong thresholds → noise.
- Taxonomy regressions: renaming or splitting classes breaks historical comparability.
- AI-on-AI spiral: LLM critics misclassify and teach the system wrong notions of “good”. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)

6) **Determinism**

- Fully deterministic if:
  - Inputs (prose, evaluator configs) are fixed.
  - Evaluators are deterministic (rule-based or LLM with temperature 0 and fixed prompts). [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)

7) **Remaining nondeterminism**

- If any evaluator uses an LLM at non-zero temperature or calls external data, verdicts may vary run-to-run. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)

8) **Controls to contain variance**

- Use:
  - Temperature 0 for LLM evaluators.
  - Fixed prompts and system messages.
  - Majority vote over N runs only during sandbox experimentation, not in production. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
- Freeze the failure taxonomy between releases and change only via governance workflows.

***

## 2. Benchmark expansion systems

### 2.1 Pattern: Failure-to-Fixture Promotion

1) **System design pattern**

- Every validated “interesting” failure is turned into a new regression fixture and added to the benchmark_fixture_library.
- Fixtures are stratified by domain, style, and failure_type. [dev](https://dev.to/hybridtechie/ai-regression-tests-written-in-markdown-not-code-5b09)

2) **Why it works / fails**

- Works:
  - System’s evaluation surface grows in exactly the directions where it previously failed.
- Fails:
  - If fixture growth is uncontrolled, you get bloated suites and flaky evaluations.
  - Overfitting: system optimizes heavily for historically failed cases and drifts elsewhere. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)

3) **Implementation in subagent architecture**

- **Failure triage subagent**:
  - Clusters similar failures (e.g., embedding-based) to propose representative failures. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
- **Fixture authoring subagent**:
  - Generates a minimal fixture description: prompt, constraints, expected qualities.
- **Human curator operator**:
  - Must approve fixture promotion (never automate fully).
- **Benchmark registry subagent**:
  - Writes to benchmark_fixture_library with versioned fixture ids.

4) **Required artifacts**

- `benchmark_fixtures/`:
  - `fixture_<id>.json` containing prompt, expected style tags, evaluation config.
- `fixture_promotion_log.jsonl`:
  - Trace from failure_id → fixture_id, plus curator decisions.

5) **Risks and failure cases**

- Fixture duplication; minor variations increase runtime but add little analytic value.
- Bias: user or domain skew leads to overrepresentation of specific styles or topics.
- Concealed regressions if new fixtures are added but old ones are silently allowed to fail.

6) **Determinism**

- Deterministic promotion path if:
  - The triage subagent’s clustering and ranking are fixed (e.g., deterministic embeddings or cached vectors).
- Human approvals are “external” but the system execution remains deterministic once the fixture set is defined.

7) **Remaining nondeterminism**

- Any LLM used for fixture generation itself; this occurs in sandbox, not in production regression suites.

8) **Controls to contain variance**

- Require:
  - Human approval for fixture inclusion.
  - “Fixture budget” per release (e.g., max new fixtures).
  - Periodic deduplication by deterministic similarity thresholds.

***

## 3. Regression testing for prose

### 3.1 Pattern: Multi-Metric Prose Regression Suite

1) **System design pattern**

- For each fixture, run:
  - Style similarity to reference samples.
  - Coherence and entity-consistency metrics. [pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/29498422/)
  - Task adequacy / content correctness (LLM-as-judge + rule-based checks). [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)
- Evaluate at feature-level, not exact text match, to avoid overconstraining creativity. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)

2) **Why it works / fails**

- Works:
  - Preserves style and quality across model or policy changes while allowing new phrasing.
- Fails:
  - Poor metrics, e.g., naïve cosine similarity between embeddings often confuses similar wording with divergent meaning. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
  - Single aggregate score hides trade-offs across dimensions.

3) **Implementation in subagent architecture**

- **Regression runner subagent**:
  - For each fixture, runs the full multi-pass pipeline and collects outputs.
- **Evaluator subagents**:
  - Style critic, coherence critic, factual critic, constraint checker.
- **Aggregation subagent**:
  - Generates per-dimension scores and flags regressions vs baseline. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)

4) **Required artifacts**

- `regression_run_<version>.json`:
  - For all fixtures, capture input, outputs, scores by dimension.
- `baseline_scores.json`:
  - Frozen reference per fixture and dimension.
- `regression_diff_report.json`:
  - Highlights per-dimension deltas and significance.

5) **Risks and failure cases**

- Drift in evaluators changes interpretation of scores; you need frozen evaluator configs per baseline. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)
- Over-reliance on LLM-as-judge metrics with hidden biases. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
- Slow runtime for large suites.

6) **Determinism**

- If:
  - Generation is constrained (temperature 0, deterministic tools).
  - Evaluators are deterministic.
  - You can treat outputs as deterministic functions of inputs. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)

7) **Remaining nondeterminism**

- Underlying LLM may be non-deterministic even at temperature 0 (hardware or vendor variance), so outputs may occasionally differ. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)

8) **Controls to contain variance**

- Use:
  - Fixed seeds where vendor allows.
  - Output canonicalization (e.g., whitespace-stripping) before hashing.
  - Tolerance bands on metrics (e.g., ±0.02) instead of hard binary pass/fail.

***

## 4. Controlled system updates (governance)

### 4.1 Pattern: Governance Gate with Sandbox → Shadow → Promote

1) **System design pattern**

- Each change to:
  - prompts, routing logic, enforcement rules, evaluators, or subagent coordination
  must pass three phases:
  - Sandbox: run on curated benchmarks and synthetic scenarios.
  - Shadow: run in parallel with production, no user-facing changes.
  - Promote/Reject: based on regression outcomes and governance rules. [docs.databricks](https://docs.databricks.com/aws/en/generative-ai/guide/agent-system-design-patterns)

2) **Why it works / fails**

- Works:
  - Prevents sudden style drift or qualitative regressions.
  - Makes system behavior auditable and revertible. [docs.databricks](https://docs.databricks.com/aws/en/generative-ai/guide/agent-system-design-patterns)
- Fails:
  - If criteria are vague or easy to override “just this once”.
  - If benchmark coverage is weak.

3) **Implementation in subagent architecture**

- **Change proposal subagent**:
  - Encodes a “system change proposal” (SCP) with diffs, rationale, and expected effects.
- **Governance evaluation subagent**:
  - Runs benchmark replays in sandbox and shadow modes and aggregates metrics.
- **Rule update subagent**:
  - Applies approved changes to policies, config files, or schemas.

4) **Required artifacts**

- `system_change_proposal_<id>.json`:
  - Contains: change_type, diff, affected components, expected risk, target metrics.
- `sandbox_eval_report_<id>.json`, `shadow_eval_report_<id>.json`.
- Governance decision record:
  - `governance_decision_<id>.json` with “promoted”, “sandboxed”, or “rejected”.

5) **Risks and failure cases**

- Governance capture: same people/agents both propose and approve changes.
- Process fatigue: manual approvals rubber-stamped.
- Hidden couplings (a style rule change unexpectedly harms coherence).

6) **Determinism**

- Governance flow itself is deterministic if:
  - Approval rules and thresholds are encoded as deterministic logic.
  - Human approvals are explicit and recorded.

7) **Remaining nondeterminism**

- Drift in human preference over time is not deterministic by design.
- Changes in external dependencies (LLM version upgrades) make behavior shift despite unchanged logic. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)

8) **Controls to contain variance**

- Require:
  - Dual control (at least two human approvers) for high-impact changes.
  - Automatic rollback if post-promotion monitoring detects anomalies.
  - Explicit tying of SCPs to model versions and evaluator versions.

***

## 5. Preventing AI-on-AI degradation loops

### 5.1 Pattern: One-Way Influence Boundary

1) **System design pattern**

- LLMs can be **judged** by automated metrics or LLM critics, but cannot directly update:
  - style rules,
  - templates,
  - or benchmark expectations.
- All changes proposed by AI must go through human-curated governance and be logged. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)

2) **Why it works / fails**

- Works:
  - Prevents critics’ biases and errors from propagating unchecked.
  - Avoids ceremonialization, where models learn to “appease” evaluators instead of writing well. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)
- Fails:
  - If humans blindly accept AI suggestions, de facto loop still exists.

3) **Implementation in subagent architecture**

- **Reflection subagents** (Reflexion-style) run only in:
  - sandboxed self-improvement loops, never in production. [arxiv](https://arxiv.org/pdf/2405.06682.pdf)
- **Rule proposal subagent**:
  - Can draft new rules or templates but cannot merge them.
- **Governance subagent**:
  - Requires human approval; only this subagent may write into rule files.

4) **Required artifacts**

- `ai_proposed_rule_updates.jsonl`:
  - Includes reasoning, suggested changes, and affected metrics.
- `human_decision_annotations.jsonl`:
  - Human notes on why suggestions were accepted or rejected.

5) **Risks and failure cases**

- AI proposals gradually shape human priors, causing subtle style homogenization.
- Overuse of LLM-as-judge leads to emergent alignment on bland “safe” prose. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)

6) **Determinism**

- Deterministic boundary enforcement if:
  - Only governance-approved rule sets are loaded at runtime.
  - The system never reads AI proposals as “source of truth”.

7) **Remaining nondeterminism**

- Human evaluators’ changing tastes.
- Variability in sandbox runs used to motivate rule changes.

8) **Controls to contain variance**

- Rotate human reviewers.
- Use diverse evaluation sources (humans from different backgrounds, external readers).
- Track “style diversity” metrics across time and raise alerts if they collapse.

***

## 6. Detecting systemic vs one-off failures

### 6.1 Pattern: Failure Clustering and Incidence Analysis

1) **System design pattern**

- Periodically cluster failure_log entries by:
  - fixture, genre, style tags, failure_type, and model version.
- Compute incidence rates and identify statistically significant spikes. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)

2) **Why it works / fails**

- Works:
  - Systemic issues show up as clusters or spikes in similar contexts.
- Fails:
  - Poor clustering features or thresholds can misclassify noise as systemic. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)

3) **Implementation in subagent architecture**

- **Failure analytics subagent**:
  - Runs periodic jobs over the failure ledger, producing cluster summaries.
- **Alerting subagent**:
  - Emits “systemic failure alerts” when thresholds cross.

4) **Required artifacts**

- `systemic_failure_clusters_<period>.json`:
  - Clusters with representative failures, statistics, and trend indicators.
- `alerts.jsonl`:
  - Machine- and human-readable alert records.

5) **Risks and failure cases**

- Overreliance on clustering; may miss subtle but important shifts.
- False positives causing change fatigue.

6) **Determinism**

- Deterministic using fixed algorithms (e.g., deterministic clustering with fixed random seeds and parameters).

7) **Remaining nondeterminism**

- If LLM-based “similarity” judgments are used, clusters may change over runs.

8) **Controls to contain variance**

- Use deterministic vector embeddings and algorithms for primary clustering.
- LLMs only for post-hoc labeling of cluster themes, not for the clustering itself.

***

## 7. Preserving voice and originality / preventing style homogenization

### 7.1 Pattern: Style Fingerprint + Diversity Constraints

1) **System design pattern**

- Maintain a **style fingerprint** per target voice:
  - distributions over sentence length, syntactic complexity, entity reuse patterns, and rhetorical structures. [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)
- Enforce constraints during evaluation:
  - penalty if outputs collapse toward global averages. [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)

2) **Why it works / fails**

- Works:
  - Tracks structural properties rather than keyword-level tokens, preserving unique voice trajectories. [pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/29498422/)
- Fails:
  - If fingerprints are too tight, they overconstrain creativity and make writing formulaic.

3) **Implementation in subagent architecture**

- **Continuity subagent**:
  - Fetches style fingerprint from continuity_state_library for the current persona/document.
- **Style evaluation subagent**:
  - Compares new outputs against fingerprint and yields a “style conformity score”.
- **Enforcement subagent**:
  - Can request regeneration of a segment that violates style bounds.

4) **Required artifacts**

- `style_fingerprint_<persona>.json`:
  - Encodes target distributions and thresholds.
- `style_score_log.jsonl`:
  - Scores per output, used to detect drift.

5) **Risks and failure cases**

- Fingerprints derived from narrow samples or already homogenized output.
- Gradual creep of fingerprints if retrained naively on new outputs.

6) **Determinism**

- Fingerprint lookup and scoring are deterministic numeric computations.

7) **Remaining nondeterminism**

- Underlying LLM’s syntactic choices still vary; style enforcement acts as a “filter”, not a strict generator.

8) **Controls to contain variance**

- Freeze fingerprints per version; update only via governance.
- Use multiple reference corpora per persona to avoid overfitting to a single sample.

***

## 8. Multi-pass writing pipelines and role separation

### 8.1 Pattern: Generate → Refine → Enforce

1) **System design pattern**

- Pipeline stages:
  - Generation: write raw draft within content constraints.
  - Refinement: revise for coherence, pacing, entity consistency, and style. [pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/29498422/)
  - Enforcement: apply rule-based corrections and safety constraints.

2) **Why it works / fails**

- Works:
  - Separation of concerns simplifies each subagent’s responsibilities.
  - Enables targeted regression testing per stage. [blog.alexewerlof](https://blog.alexewerlof.com/p/ai-systems-engineering-patterns)
- Fails:
  - Overcorrection in enforcement can flatten style.
  - Repeated refinement stages risk drift from original intent.

3) **Implementation in subagent architecture**

- **Generation agent**:
  - Access to prompt, constraints, and continuity_state_library.
- **Refinement agent**:
  - Receives draft and state; may add bridging text or rephrase segments.
- **Enforcement agent**:
  - Applies only deterministic transformations (e.g., forbidden pattern removal, style rule patches).

4) **Required artifacts**

- Stage-specific logs:
  - `draft_output.json`, `refined_output.json`, `final_output.json`.
- Stage metrics:
  - e.g., coherence score change between draft and refined.

5) **Risks and failure cases**

- Infinite loops if refinement repeatedly oscillates on “better” vs “worse”.
- Inter-stage disagreement about style or constraints.

6) **Determinism**

- If all stages are single-pass, temperature 0, and free of external IO, the pipeline is deterministic.

7) **Remaining nondeterminism**

- Underlying LLM still may introduce minor variance.
- Error-handling branches triggered only under rare conditions.

8) **Controls to contain variance**

- Hard cap on refinement passes.
- Strict interface contracts between stages (schemas and invariants).

***

## 9. Runtime enforcement of style consistency

### 9.1 Approaches and tradeoffs

| Approach            | Determinism | Strengths                                             | Weaknesses                                      |
|---------------------|------------|-------------------------------------------------------|-------------------------------------------------|
| Rule-based          | High       | Transparent, predictable, easy to test.  [lcs.ios.ac](http://lcs.ios.ac.cn/~znj/papers/Runtime_Enforcement_againt_STL___Camera_Ready_Version.pdf)      | Hard to encode nuanced style, brittle rules.    |
| Structured critics  | Medium     | Structured scores, good for prose metrics.  [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)   | May still rely on ML components.                |
| LLM-as-judge        | Low–Med    | Flexible, captures nuance.  [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)                   | Non-deterministic, prompt-sensitive.            |
| Hybrid (rules+LLM)  | Medium     | Rules guardrails + nuanced scoring.  [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)  | Complexity, risk of silent drift in LLM part.   |

- For deterministic systems:
  - Style enforcement should be rule-based or hybrid, where LLMs only generate scores offline, and thresholds are frozen per version. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)
- Runtime:
  - Use rule-based checks and numeric thresholds; no LLM-in-the-loop enforcement for production determinism.

***

## 10. State-based tracking for long-form coherence

### 10.1 Pattern: Entity and Thread Memory

1) **System design pattern**

- Maintain a structured **narrative state**:
  - Entities (name, attributes, relationships), open threads (goals, conflicts), time/scene index. [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)
- Continuity_state_library stores and retrieves this state per document or series.

2) **Why it works / fails**

- Works:
  - Enforces consistent entity usage and long-range coherence beyond context window. [pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/29498422/)
- Fails:
  - If state is incomplete or wrong, enforcement locks in errors.

3) **Implementation in subagent architecture**

- **State builder subagent**:
  - Parses generated text into structured state updates. [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)
- **Continuity subagent**:
  - Provides state snapshots to generation and refinement agents.
- **Coherence evaluator subagent**:
  - Checks new segments against state and flags inconsistencies.

4) **Required artifacts**

- `continuity_state_<doc_id>.json`:
  - E.g., entity graphs, thread status, timeline markers.
- `state_diff_<segment>.json`:
  - Changes proposed and applied per output chunk.

5) **Risks and failure cases**

- State explosion for very long works.
- Hard-to-resolve conflicts if earlier errors propagate.

6) **Determinism**

- State transitions are deterministic functions of prior state and segment text.

7) **Remaining nondeterminism**

- Initial generation still subject to LLM variance, which shapes state trajectory.

8) **Controls to contain variance**

- Use deterministic parsers where possible.
- Limit the types of state changes allowed per segment (e.g., no retroactive entity deletions).

***

## 11. Neuro-symbolic / hybrid architectures

### 11.1 Pattern: Symbolic Shell over Neural Core

1) **System design pattern**

- Neural components:
  - LLM for drafting, rewriting.
- Symbolic components:
  - Rule-based validators, continuity state, style fingerprints, governance logic.
- All orchestration, state transitions, and enforcement handled symbolically. [blog.alexewerlof](https://blog.alexewerlof.com/p/ai-systems-engineering-patterns)

2) **Why it works / fails**

- Works:
  - Gains LLM creativity while keeping control and determinism in the symbolic shell. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)
- Fails:
  - If symbolic layer is too weak, neural core’s variability leaks into user-facing outputs.

3) **Implementation in subagent architecture**

- **Neural subagents**:
  - Generation, refinement, and optional critics.
- **Symbolic subagents**:
  - Rule enforcement, state management, regression checks, governance.

4) **Required artifacts**

- Schema contracts for I/O between neural and symbolic parts.
- Versioned rule sets and policies.

5) **Risks and failure cases**

- Mismatch between symbolic representation and the nuances of text.
- Symbolic rules that conflict with each other.

6) **Determinism**

- Symbolic control ensures that given the same neural outputs, decisions are deterministic.
- Overall system quasi-deterministic if LLM behavior is stable enough across runs. [reddit](https://www.reddit.com/r/AI_Agents/comments/1pv2gfk/how_do_you_make_agents_deterministic/)

7) **Remaining nondeterminism**

- Non-deterministic generation from LLM, especially for open-ended prompts.

8) **Controls to contain variance**

- Constrain prompts, use temperature 0, and enforce tight acceptance criteria through symbolic validators.

***

## 12. Example JSON / state contracts

### 12.1 Subagent coordination contract

```json
{
  "request_id": "req-123",
  "doc_id": "novel-42",
  "stage": "generation",
  "input_prompt": "...",
  "constraints": {
    "persona": "noir_detective",
    "max_tokens": 800
  },
  "continuity_state_ref": "continuity_state_novel-42_v3",
  "style_fingerprint_ref": "style_fingerprint_noir_detective_v2"
}
```

```json
{
  "request_id": "req-123",
  "stage": "generation",
  "output_text": "...",
  "metadata": {
    "model_version": "llm-v5.1",
    "temperature": 0
  }
}
```

### 12.2 Continuity state contract

```json
{
  "continuity_state_id": "continuity_state_novel-42_v3",
  "entities": [
    {
      "entity_id": "e1",
      "name": "Detective Hale",
      "attributes": {
        "age": 43,
        "occupation": "detective",
        "injury_status": "broken arm"
      },
      "last_seen_chapter": 5
    }
  ],
  "threads": [
    {
      "thread_id": "t1",
      "description": "Solve the warehouse murder",
      "status": "ongoing",
      "opened_chapter": 1,
      "target_resolution_chapter": 10
    }
  ],
  "style_context": {
    "persona": "noir_detective",
    "style_fingerprint_ref": "style_fingerprint_noir_detective_v2"
  }
}
```

***

## 13. Governance: self-improvement loops and promotion criteria

### 13.1 Governed self-improvement loop

1) **Phases**

- **Learn** (sandbox only):
  - Run new prompts, Reflexion-style self-reflection, or new evaluators on captured failures and benchmarks. [youtube](https://www.youtube.com/watch?v=VCPwYAQTcpE)
- **Propose**:
  - Subagents generate change proposals (new rules, prompts, heuristics) with predicted effects.
- **Evaluate**:
  - Run full benchmark replays and additional stress tests with new configuration. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)
- **Decide**:
  - Governance gate decides promote, keep sandboxed, or reject.

2) **Subagents**

- **Evaluation subagent**:
  - Executes benchmark suite and computes multi-dimensional scores.
- **Failure taxonomy subagent**:
  - Updates coverage statistics on failure types.
- **Rule update subagent**:
  - Prepares candidate changes, never applies them directly.
- **Regression checking subagent**:
  - Compares candidate vs baseline on all dimensions.

3) **What should NEVER be fully automated**

- Final:
  - Rule acceptance for style, safety, or persona definitions.
  - Benchmark addition/removal decisions.
  - Overrides of regression failures.
- Human should:
  - Approve or reject proposals based on contextual understanding and long-term style goals.

### 13.2 Promotion / sandbox / rejection criteria

- **Promote** when:
  - No statistically significant regressions on safety-related metrics.
  - Net improvement on targeted failure modes.
  - No unacceptable loss on style or coherence outside pre-agreed tradeoff bands. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)
- **Sandbox-only** when:
  - Gains are promising but regressions exist in non-critical dimensions.
  - More data or metrics are required.
- **Reject** when:
  - Critical regressions (safety, core persona violation).
  - Gains confined to rare or low-value scenarios but costs are broad.

### 13.3 Benchmark replay requirements

- Must run:
  - Full benchmark_fixture_library for the relevant persona/domain.
  - Stress tests for known edge cases and failure modes. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)
- Replays must include:
  - Baseline vs candidate outputs, metrics, and diff reports.

### 13.4 Multi-dimensional regression detection

- For each fixture:
  - Track scores for style, coherence, factuality, safety, and originality.
- Regression checker must:
  - Flag “Pareto-unsafe” changes: improvements in one dimension that push another below minimum thresholds.
- Provide:
  - Clear per-dimension deltas in reports so humans can make informed tradeoffs.

***

## 14. Validation approaches and determinism boundaries

### 14.1 Rule-based systems

- Deterministic, composable, easy to regression-test. [lcs.ios.ac](http://lcs.ios.ac.cn/~znj/papers/Runtime_Enforcement_againt_STL___Camera_Ready_Version.pdf)
- Limited expressive power for nuanced narrative style.

### 14.2 Structured critics

- Use neural models or feature extractors to produce numeric scores for specific aspects (e.g., entity coherence). [pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/29498422/)
- Deterministic if model and environment are fixed, but brittle if distribution shifts.

### 14.3 LLM-as-judge

- Flexible, good for semantic similarity, style judgments. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
- Non-deterministic and prompt-sensitive; best confined to sandbox evaluation. [vikasgoyal.github](https://vikasgoyal.github.io/agentic/observe/evalstesting.html)

### 14.4 Hybrid evaluators

- Combine:
  - Rules for hard constraints.
  - Structured critics or LLM judges for soft ones. [towardsdatascience](https://towardsdatascience.com/how-we-are-testing-our-agents-in-dev/)
- Determinism tradeoff:
  - Soft components must be frozen or run multiple times to estimate stable scores.

***

## 15. Reflexion-style self-reflection in writing agents

### 15.1 Diagnosis value vs risks

- **Benefits**:
  - Can identify patterns in errors and suggest corrections. [arxiv](https://arxiv.org/pdf/2405.06682.pdf)
- **Risks**:
  - Self-referential loops that cause the model to learn to “sound reflective” rather than improve.
  - Drift of style toward generic “explanatory” tone influenced by reflections. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)

### 15.2 Determinism and boundaries

- Should:
  - Exist only inside sandboxed improvement loops, never in production writing.
- Reflections:
  - Treated as **data** for humans and governance processes, not as direct rule updates.

***

## 16. Library extraction blocks

### RULESET_EXTRACT

- Style rule sets:
  - Persona-specific fingerprints and constraints in system_design_library and continuity_state_library.
- Enforcement rules:
  - Deterministic, rule-based checks for forbidden patterns, structural constraints, and minimal style conformity.
- Governance rules:
  - Promotion criteria, regression thresholds, and approval workflows encoded as machine-readable policies in system_design_library.

### OPERATOR_EXTRACT

- Human operators:
  - Approve rule changes, benchmark promotions, and high-impact system updates.
  - Review AI-derived reflections and proposals.
- Operational subagents:
  - Execution, logging, evaluation, analytics, and governance subagents coordinated via strict JSON contracts.

### FAILURE_MODE_EXTRACT

- Failure_mode_library:
  - Contains normalized categories for:
    - Generic or bland writing.
    - Style drift vs target persona.
    - Entity inconsistency and coherence breaks. [proceedings.mlr](https://proceedings.mlr.press/v162/papalampidi22a/papalampidi22a.pdf)
    - Hallucination and misalignment. [ceaksan](https://ceaksan.com/en/llm-behavioral-failure-modes/)
- Each failure mode:
  - Bound to detection logic, example fixtures, and regression checks.

### TEST_CASE_EXTRACT

- benchmark_fixture_library:
  - Stores fixtures derived from real failures and curated benchmarks, each with:
    - Input prompt, constraints, expected style and quality tags, evaluation config.
- Regression test cases:
  - Multi-dimensional evaluation (style, coherence, factuality, safety, originality) with frozen baselines and tolerance bands.

### LIBRARY_EXTRACT

- system_design_library:
  - Agent orchestration patterns, multi-pass pipelines, governance workflows, configuration schemas.
- failure_mode_library:
  - Failure taxonomy, detection rules, cluster analytics.
- benchmark_fixture_library:
  - Versioned fixtures and replay suites.
- evaluation_library:
  - Rule-based validators, structured critics, LLM-as-judge wrappers, and hybrid evaluators.
- continuity_state_library:
  - Narrative state representations (entities, threads, style context), continuity snapshots, and state-diff records. [pubmed.ncbi.nlm.nih](https://pubmed.ncbi.nlm.nih.gov/29498422/)


## RULESET_EXTRACT
RULE-SD-1: All production evaluation paths must be deterministic for fixed inputs, versions, and configuration.
RULE-SD-2: Every detected failure must be logged to an append-only structured failure ledger.
RULE-SD-3: Failure taxonomy changes must be versioned and may not silently rewrite historical labels.
RULE-SD-4: Only validated failures may be promoted into benchmark fixtures.
RULE-SD-5: Benchmark promotion requires human approval before a fixture becomes part of replayable suites.
RULE-SD-6: Regression suites must score outputs across multiple dimensions rather than a single aggregate score alone.
RULE-SD-7: Evaluator prompts, thresholds, and model versions must be frozen for any baseline used in promotion decisions.
RULE-SD-8: System changes must pass sandbox evaluation before shadow evaluation.
RULE-SD-9: No change may be promoted to production without benchmark replay against the relevant fixture set.
RULE-SD-10: AI-generated reflections or rule proposals may never directly modify production rules.
RULE-SD-11: Human approval is mandatory for rule acceptance, benchmark promotion, and override of critical regressions.
RULE-SD-12: Systemic-versus-one-off failure classification must use deterministic clustering or deterministic feature analytics in primary workflows.
RULE-SD-13: Style fingerprints must be versioned and frozen between releases unless changed through governance.
RULE-SD-14: Multi-pass pipelines must preserve strict schema contracts between generation, refinement, and enforcement stages.
RULE-SD-15: Production runtime style enforcement must be rule-based or use frozen numeric thresholds from hybrid evaluators.
RULE-SD-16: Long-form coherence must be backed by structured continuity state rather than raw-context recall alone.
RULE-SD-17: State transitions must be logged as explicit diffs and may not retroactively rewrite canonical state without governance.
RULE-SD-18: Reflexion-style self-reflection may run only in sandboxed improvement loops, never as a live production writer or updater.
RULE-SD-19: Promotion decisions must reject Pareto-unsafe changes that improve one dimension while dropping another below minimum thresholds.
RULE-SD-20: External dependency changes, including evaluator or model-version changes, require fresh benchmark replay before promotion.

## OPERATOR_EXTRACT
OP-SD-1: Write every failure event to `failure_log.jsonl` with fixture id, pipeline stage, version metadata, evaluator outputs, and resolution state.
OP-SD-2: Maintain `failure_taxonomy.json` as a controlled vocabulary with explicit versioning.
OP-SD-3: Cluster failure-ledger entries periodically to identify systemic spikes by fixture, genre, style, failure type, and model version.
OP-SD-4: Convert approved representative failures into versioned benchmark fixtures and record failure-to-fixture lineage.
OP-SD-5: Run multi-metric regression suites on frozen fixtures before any architecture, prompt, rule, or model change is promoted.
OP-SD-6: Generate `system_change_proposal` artifacts for every candidate update and route them through sandbox then shadow evaluation.
OP-SD-7: Freeze evaluator prompts, thresholds, and configs per release so score comparisons remain historically meaningful.
OP-SD-8: Keep AI-generated rule or prompt proposals in proposal logs only until human approval occurs.
OP-SD-9: Compute style-conformity scores against frozen style fingerprints and log drift over time.
OP-SD-10: Cap refinement passes and preserve stage-separated artifacts for generation, refinement, and enforcement outputs.
OP-SD-11: Load continuity state snapshots before generation or refinement and emit deterministic `state_diff` artifacts after each segment.
OP-SD-12: Use rule-based checks in production runtime; confine LLM-as-judge and Reflexion-style loops to sandbox analysis unless explicitly frozen and approved.

## FAILURE_MODE_EXTRACT
FM-SD-1: Failure-ledger noise collapse caused by over-broad taxonomy or noisy evaluators.
FM-SD-2: Failure-to-fixture bloat caused by uncontrolled promotion and duplicate fixtures.
FM-SD-3: Benchmark overfitting where the system optimizes to historical fixtures but drifts elsewhere.
FM-SD-4: Evaluator drift that invalidates baseline comparisons across releases.
FM-SD-5: Governance capture where proposal and approval paths are not sufficiently separated.
FM-SD-6: Rubber-stamp governance fatigue that lets regressions through.
FM-SD-7: AI-on-AI degradation where evaluator or reflection bias shapes production rules indirectly.
FM-SD-8: Systemic-failure false positives caused by unstable clustering features or thresholds.
FM-SD-9: Style fingerprint overconstraint that preserves sameness instead of voice.
FM-SD-10: Style fingerprint creep caused by retraining on already-homogenized outputs.
FM-SD-11: Multi-pass oscillation where refinement loops endlessly or degrades original intent.
FM-SD-12: Production style-flattening caused by overpowered enforcement stages.
FM-SD-13: Continuity lock-in where incorrect state is preserved and enforced downstream.
FM-SD-14: State explosion that makes long-form continuity unmanageable or too costly.
FM-SD-15: Hybrid-evaluator silent drift where soft components shift behavior without governance.
FM-SD-16: Stable-but-wrong promotion where deterministic outputs still fail core quality or correctness goals.
FM-SD-17: Reflection-style tone contamination where sandbox reflections bias prose toward explanatory blandness.

## TEST_CASE_EXTRACT
TC-SD-1: Replay a fixed failure corpus twice and verify the failure ledger produces identical structured entries under frozen configs.
TC-SD-2: Submit duplicate failure cases to fixture-promotion flow and verify deterministic deduplication prevents benchmark bloat.
TC-SD-3: Run a candidate update that improves target failures but harms style metrics and confirm governance marks it Pareto-unsafe.
TC-SD-4: Change evaluator prompts without version bump and verify baseline-comparison checks fail the promotion pipeline.
TC-SD-5: Inject an AI-generated rule proposal into production-rule paths and verify one-way influence boundaries block it.
TC-SD-6: Feed clustered one-off failures and true systemic spikes into analytics and verify deterministic clustering distinguishes them.
TC-SD-7: Run outputs against frozen style fingerprints and confirm style drift is flagged while approved intentional shifts remain allowed only through governance.
TC-SD-8: Force repeated refinement passes and verify pass caps plus stage-contract checks prevent oscillation loops.
TC-SD-9: Seed contradictory entity updates into continuity state and verify state-diff and coherence checks block illegal transitions.
TC-SD-10: Compare rule-based, structured-critic, LLM-judge, and hybrid evaluators on the same fixture set and verify determinism boundaries are reported correctly.
TC-SD-11: Run Reflexion-style sandbox loops and verify their proposals are logged as data only and cannot update live runtime.
TC-SD-12: Execute sandbox, shadow, and promotion stages for a system change and verify artifact lineage is complete and promotion criteria are enforced.

## LIBRARY_EXTRACT
system_design_library
failure_ledger_schema
fixture_promotion_workflow
multi_metric_regression_workflow
governance_gate_workflow
one_way_influence_boundary
systemic_failure_clustering_policy
multi_pass_pipeline_contract
hybrid_evaluator_policy
promotion_decision_policy
failure_mode_library
failure_ledger_noise_collapse
benchmark_bloat_failure
benchmark_overfit_failure
evaluator_drift_failure
governance_capture_failure
ai_on_ai_degradation_failure
clustering_false_positive_failure
style_fingerprint_creep
refinement_oscillation_failure
continuity_lock_in_failure
stable_but_wrong_pattern
reflection_tone_contamination
benchmark_fixture_library
failure_replay_suite
fixture_dedup_suite
pareto_tradeoff_suite
evaluator_versioning_suite
one_way_boundary_suite
systemic_failure_cluster_suite
style_drift_regression_suite
refinement_loop_suite
continuity_state_conflict_suite
governance_promotion_suite
evaluation_library
deterministic_regression_runner
style_conformity_scorer
coherence_regression_checker
pareto_tradeoff_checker
evaluator_drift_checker
clustering_analytics_runner
continuity_state_checker
hybrid_evaluator_wrapper
continuity_state_library
entity_thread_memory_state
continuity_state_snapshot
continuity_state_diff_schema
style_fingerprint_state
thread_status_registry
scene_transition_state