# Benchmark Alignment Report

## Scope

- `libraries/benchmark_fixture_library/entries/v6_adversarial_viral_suite.json`
- `runtime/validation/validator_registry.json`
- `runtime/validation/evaluation_thresholds.json`
- `evaluation/reports/evaluation_report.template.json`

## Result

- Misalignments found: 2
- Validator logic changed: no
- Benchmark expectations updated: yes
- Fixtures flagged for validator review: 0

## Fixture Review

### v6_viral_integrity_fail_001

- Expected gating before audit: `rejected`
- Actual gating: `rejected`
- Expected mismatch source: benchmark omitted insight-density behavior
- Actual insight-density evidence:
  - `insight_density_score: 0.34`
  - `abstraction_ratio: 0.0`
  - `concrete_example_count: 1`
  - `empty_insight: true`
- Audit decision: update benchmark expectations

Rationale:

The fixture is still correctly rejected for viral-integrity reasons, and the low insight-density signal is also correct. This is not a validator bug. The benchmark was simply missing the v6.1 expectation layer.

### v6_viral_integrity_pass_001

- Expected gating before audit: `accepted_with_warnings`
- Actual gating: `accepted_with_warnings`
- Expected mismatch source: benchmark omitted insight-density and other active v6 validator outcomes
- Actual insight-density evidence:
  - `insight_density_score: 0.6`
  - `abstraction_ratio: 0.5`
  - `concrete_example_count: 4`
  - `generic_motivation: false`
  - `empty_insight: false`
  - `shallow_philosophy: false`
- Audit decision: update benchmark expectations

Rationale:

The validator behavior is internally consistent. The passage carries real evidence and avoids the low-value failure modes. The benchmark now reflects the current deterministic stack rather than the earlier, narrower viral-integrity-only expectation.

## Alignment Decision

All identified mismatches were benchmark expectation gaps caused by the addition of InsightDensityValidator. No mismatch required a validator change, and no fixture was flagged for review.

## Fields Added To Fixtures

- `expected_metric_fields.insight_density_score`
- `expected_metric_fields.abstraction_ratio`
- `expected_metric_fields.concrete_example_count`
- `expected_signals.generic_motivation`
- `expected_signals.empty_insight`
- `expected_signals.shallow_philosophy`
- `expected_failure_modes`

## Conclusion

Benchmark alignment has been restored without weakening InsightDensityValidator. The adversarial suite now reflects the current runtime behavior and preserves the original adversarial strength.
