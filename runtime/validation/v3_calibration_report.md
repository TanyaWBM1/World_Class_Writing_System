# SemanticRedundancyValidator v3 Calibration Report

## Scope

- Primary suite: `redundancy_v2_adversarial_suite`
- Regression suites: `cadence_stress_suite`, `dialogue_realism_suite`
- Calibration target: balance legitimate recurrence, refrain handling, motif return, and collapse detection without changing architecture

## Before vs After

- Adversarial class matches before calibration: `4/7`
- Adversarial class matches after calibration: `7/7`
- Adversarial gating matches before calibration: `6/7`
- Adversarial gating matches after calibration: `7/7`
- Cadence stress suite after calibration: `4/4` fixture matches
- Dialogue realism suite after calibration: `4/4` fixture matches

## False Positive Reduction

- `redundancy_v2_emotion_001` moved from `refrain_like` to `legitimate_recurrence`
- `redundancy_v2_spin_001` moved from `refrain_like` to `semantic_spin`
- `cadence_adversarial_001` moved from semantic redundancy `fail` to `warn`

## False Negative Reduction

- `redundancy_v2_collapse_001` moved from `clean_progression` / `accepted` to `collapse` / `rejected`

## Calibration Notes

- Modal-heavy threat loops no longer receive progression credit simply for containing causal-looking auxiliaries.
- Emotional circling now earns legitimate recurrence classification when emotion-state transitions are present without literal refrain markers.
- Cadence-driven refrain pressure now receives bounded downgrade relief so cadence stress no longer creates semantic collapse by itself.
- Cluster-overuse and collapse-risk thresholds now trigger earlier for high-risk global and local recurrence patterns.
