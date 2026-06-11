# Calibration Summary

## Coverage

- Indexed suites executed: 6
- Fixtures executed: 24
- Targeted classification accuracy after calibration: 24/24

## Threshold Calibration Outcome

- Cadence fail floor was lowered so low-variance but non-collapsed prose lands in warning instead of rejection.
- Abstraction thresholds now separate grounded warning cases from true abstract collapse cases.
- Semantic redundancy fail floor now reserves rejection for stronger novelty collapse while keeping adversarial repetition visible.
- Continuity warning and fail bands now reflect partial state retention versus hard contradiction.
- Dialogue realism thresholds now match the corrected utterance parsing and bridge-aware scoring model.
- Human style preference thresholds now accept strong single-paragraph prose while still rejecting list-shaped summaries.

## Residual Risks

- Benchmarks are evaluated against their targeted validators for gating to avoid unrelated validator contamination in family-specific fixtures.
- Full multi-validator end-to-end benchmark gating remains a separate calibration problem once broader fixture coverage exists for cross-dimension interactions.
