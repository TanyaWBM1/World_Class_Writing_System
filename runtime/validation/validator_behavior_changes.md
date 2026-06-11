# Validator Behavior Changes

## SemanticRedundancyValidator v3

- `clean_progression` now requires stronger role-transition support and no frame-loop collapse signature.
- `legitimate_recurrence` now recognizes emotional-state progression without forcing literal refrain detection.
- `refrain_like` now depends on actual refrain markers plus transformation, instead of broad emotional recurrence alone.
- `semantic_spin` now catches weakly transformed repeated ideas before they are mislabeled as refrain.
- `collapse` now triggers on lexical-diversity threat loops when modal repetition and semantic-frame reuse converge.

## Cross-Validator Stability

- Cadence interaction relief remains bounded and only downgrades semantic collapse when the repetition pattern is cadence-shaped rather than propositionally collapsed.
- Dialogue realism behavior was not changed in this calibration pass and remained stable across all dialogue fixtures.
- No other validator families were modified.
