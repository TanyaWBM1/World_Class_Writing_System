# Redundancy V2 Failure Report

## Scope

- Suite: `redundancy_v2_adversarial_suite`
- Validator under test: `semantic_redundancy_detector`
- Runtime mode: current deterministic validator, no v2 class implementation added in this pass

## Outcome

- Fixtures executed: 7
- Class-level mismatches: 7
- Gating mismatches: 5

## Primary Failure Boundary

- The current validator does not emit any of the required v2 redundancy classes.
- Every class comparison collapses to `unclassified_by_current_runtime`.
- This confirms the present implementation still reasons through overlap-era surrogate signals rather than explicit idea-graph relations.

## Fixture Findings

### redundancy_v2_refrain_001

- Expected class: `refrain_like`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `accepted_with_warnings`
- Actual gating: `accepted_with_warnings`
- Current score/status: `0.76` / `warn`
- Difficulty note: Repeated phrase appears four times, but each recurrence intensifies emotional pressure and changes local narrative function.

### redundancy_v2_motif_001

- Expected class: `motif_recall`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `accepted_with_warnings`
- Actual gating: `accepted`
- Current score/status: `0.86` / `pass`
- Difficulty note: The recurring object is intentional thematic recall rather than proposition collapse; the graph should create a motif node, not a restatement loop.

### redundancy_v2_dialogue_001

- Expected class: `dialogue_callback`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `accepted_with_warnings`
- Actual gating: `accepted`
- Current score/status: `0.91` / `pass`
- Difficulty note: A callback repeats the original proposition only long enough to negate and replace it.

### redundancy_v2_argument_001

- Expected class: `clean_progression`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `accepted`
- Actual gating: `accepted_with_warnings`
- Current score/status: `0.7` / `warn`
- Difficulty note: Surface continuity is high, but the causal graph should grow at each step.

### redundancy_v2_spin_001

- Expected class: `semantic_spin`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `accepted_with_warnings`
- Actual gating: `accepted_with_warnings`
- Current score/status: `0.78` / `warn`
- Difficulty note: The language mutates slightly while the idea graph should remain almost flat.

### redundancy_v2_collapse_001

- Expected class: `collapse`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `rejected`
- Actual gating: `accepted_with_warnings`
- Current score/status: `0.75` / `warn`
- Difficulty note: Phrase overlap is low, so overlap counting alone may under-detect the collapse.

### redundancy_v2_emotion_001

- Expected class: `legitimate_recurrence`
- Actual class: `unclassified_by_current_runtime`
- Expected gating: `accepted_with_warnings`
- Actual gating: `accepted`
- Current score/status: `0.91` / `pass`
- Difficulty note: Borderline case between emotional deepening and redundant circling; intended to stress class boundaries rather than raw score only.

