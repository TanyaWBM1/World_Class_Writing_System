# V2 vs V3 Comparison

## Scope

- Suite: `redundancy_v2_adversarial_suite`
- Prior baseline: `redundancy_v2_adversarial_suite` against pre-v3 runtime output
- Current contracts: `validator_registry_v4` / `evaluation_thresholds_v4`

## Classification Outcome

- Previously unclassified cases: 7
- Currently unclassified cases: 7
- Resolved unclassified cases: 0

## Targeted Improvements

- legitimate_recurrence detection improvement: no
- motif_recall detection improvement: no
- dialogue_callback detection improvement: no

## Findings

- The registry and thresholds now describe SemanticRedundancyValidator v3, but the current runtime evaluator still uses the earlier overlap-era scoring path.
- As a result, all previously unclassified cases remain unclassified by the live validator output.
- Gating behavior is unchanged from the prior run for the tracked fixtures.

## Fixture Deltas

- `redundancy_v2_refrain_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted_with_warnings` -> `accepted_with_warnings`.
- `redundancy_v2_motif_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted` -> `accepted`.
- `redundancy_v2_dialogue_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted` -> `accepted`.
- `redundancy_v2_argument_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted_with_warnings` -> `accepted_with_warnings`.
- `redundancy_v2_spin_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted_with_warnings` -> `accepted_with_warnings`.
- `redundancy_v2_collapse_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted_with_warnings` -> `accepted_with_warnings`.
- `redundancy_v2_emotion_001`: class `unclassified_by_current_runtime` -> `unclassified_by_current_runtime`, gating `accepted` -> `accepted`.
