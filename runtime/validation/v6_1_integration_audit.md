# v6.1 InsightDensityValidator Integration Audit

## Scope

- `runtime/validation/validator_registry.json`
- `runtime/validation/evaluation_thresholds.json`
- `evaluation/reports/evaluation_report.template.json`
- `libraries/benchmark_fixture_library/entries/v6_adversarial_viral_suite.json`
- `runtime/validation/validator_engine.py`

## Audit Result

- Registry wiring: confirmed
- Threshold wiring: confirmed
- Runtime scoring integration: confirmed
- Machine-readable evidence emission: confirmed
- Report field presence: confirmed
- Adversarial benchmark alignment: incomplete

## Findings

### 1. Registration

`InsightDensityValidator` is present in the validator registry as `insight_density_validator` with:

- `validator_family: viral_intelligence_stack`
- `dimension: viral_intelligence`
- `threshold_key: insight_density_validator`
- linked rule `RULE_INSIGHT_DENSITY_MIN`
- linked failure modes:
  - `generic_motivation_failure`
  - `empty_insight_failure`
  - `shallow_philosophy_failure`

It is also listed in `dimension_to_validators.viral_intelligence`.

### 2. Thresholds

`runtime/validation/evaluation_thresholds.json` defines:

- `pass_min: 0.76`
- `warn_min: 0.58`
- `fail_below: 0.58`

The validator is also included in `dimensions.viral_intelligence.driving_validators`, so it participates in dimension scoring.

### 3. Runtime Scoring

`runtime/validation/validator_engine.py` wires the insight-density layer into execution:

- `build_v6_viral_metrics(...)` computes:
  - `insight_density_score`
  - `abstraction_ratio`
  - `concrete_example_count`
  - `generic_motivation_detected`
  - `empty_insight_detected`
  - `shallow_philosophy_detected`
- `viral_score` includes `insight_density_score` in the averaged viral stack.
- `viral_integrity_score` includes a positive contribution from `insight_density_score`.
- `novelty_score` is penalized when `insight_density_score < 0.4`.
- `score_validator(...)` has a dedicated `insight_density_validator` branch that emits machine-readable evidence.

This confirms the validator is not only declared in config; it is used in execution.

### 4. Report Fields

`evaluation/reports/evaluation_report.template.json` includes:

- `insight_density_score`
- `abstraction_ratio`
- `concrete_example_count`

These fields are available at top level for downstream reporting.

### 5. Live Evidence Check

A controlled run against generic motivational content produced:

- `insight_density_score: 0.0`
- `abstraction_ratio: 1.0`
- `concrete_example_count: 0`
- `generic_motivation_detected: true`
- `empty_insight_detected: true`
- `shallow_philosophy_detected: true`
- `insight_density_validator status: fail`

This confirms the machine-readable evidence fields are populated during runtime, not just templated.

### 6. False-Positive Reduction

The validator correctly catches low-value viral-looking content associated with:

- `generic_motivation`
- `empty_insight`
- `shallow_philosophy`

The current runtime therefore reduces a class of false positives where content appears portable or emotionally legible but lacks concrete insight.

### 7. Benchmark Alignment

`libraries/benchmark_fixture_library/entries/v6_adversarial_viral_suite.json` is only partially aligned with v6.1.

Current state:

- The suite still validates adversarial viral integrity behavior.
- It does not explicitly include `InsightDensityValidator` in `expected_validator_outcomes`.
- It does not assert the insight-density evidence fields or the new low-value failure modes.

Implication:

- v6.1 runtime wiring is complete.
- adversarial benchmark expectations have not yet been upgraded to fully reflect the new validator.

## Conclusion

The InsightDensityValidator integration is operational in runtime scoring and reporting. The remaining gap is benchmark expectation coverage in `v6_adversarial_viral_suite.json`, which lags behind the implemented runtime behavior.
