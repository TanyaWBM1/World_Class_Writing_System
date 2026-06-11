# V2 vs V3 Runtime Delta

## Summary

- Previously unclassified cases: 7
- Unclassified cases after v3 activation: 0
- Resolved unclassified cases: 7
- Expected label matches: 4/7
- Expected gating matches: 6/7

## Improvements

- legitimate_recurrence detection: not improved
- motif_recall detection: improved
- dialogue_callback detection: improved

## Fixture Deltas

- `redundancy_v2_refrain_001`: class `unclassified_by_current_runtime` -> `refrain_like`, gating `accepted_with_warnings` -> `accepted_with_warnings`.
- `redundancy_v2_motif_001`: class `unclassified_by_current_runtime` -> `motif_recall`, gating `accepted` -> `accepted_with_warnings`.
- `redundancy_v2_dialogue_001`: class `unclassified_by_current_runtime` -> `dialogue_callback`, gating `accepted` -> `accepted_with_warnings`.
- `redundancy_v2_argument_001`: class `unclassified_by_current_runtime` -> `clean_progression`, gating `accepted_with_warnings` -> `accepted`.
- `redundancy_v2_spin_001`: class `unclassified_by_current_runtime` -> `refrain_like`, gating `accepted_with_warnings` -> `accepted_with_warnings`.
- `redundancy_v2_collapse_001`: class `unclassified_by_current_runtime` -> `clean_progression`, gating `accepted_with_warnings` -> `accepted`.
- `redundancy_v2_emotion_001`: class `unclassified_by_current_runtime` -> `refrain_like`, gating `accepted` -> `accepted_with_warnings`.
