# Validator Misclassification Report

## Final Status

- Targeted fixture accuracy: 24/24
- Remaining false positives: 0
- Remaining false negatives: 0

## Pre-Calibration Problem Areas

- Cadence variance over-rejected warn fixtures because the fail floor sat too close to the warning band.
- Dialogue realism undercounted utterances when multiple quoted lines appeared on one paragraph line.
- Continuity consistency treated location anchoring too literally and missed partial context retention.
- Human style preference penalized single-paragraph prose that should count as valid paragraph-first writing.
- Semantic redundancy over-penalized refrain-like repetition and under-modeled semantic frame recurrence.

## Final Misclassification Inventory

- No remaining targeted misclassifications after calibration.
