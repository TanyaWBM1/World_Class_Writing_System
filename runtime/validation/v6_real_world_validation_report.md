# V6 Real-World Validation Report

## Overview

- fixtures_run: 10
- false_positives: 0
- false_negatives: 2
- true_positives: 0
- true_negatives: 8

## High-Integrity Versus Shallow Viral Content

- high_integrity_viral favored: 0
- shallow viral-looking favored: 0
- high-integrity favored over shallow: False

## Where InsightDensityValidator Changed Final Outcomes

- `rw_generic_viral_looking_001` `generic_viral_looking` final `rejected` insight_density_score `0.0`.
- `rw_generic_viral_looking_002` `generic_viral_looking` final `rejected` insight_density_score `0.12`.
- `rw_manipulative_clickbait_002` `manipulative_clickbait` final `rejected` insight_density_score `0.058`.
- `rw_outrage_bait_001` `outrage_bait` final `rejected` insight_density_score `0.048`.
- `rw_outrage_bait_002` `outrage_bait` final `rejected` insight_density_score `0.25`.
- `rw_strong_but_nonviral_001` `strong_but_nonviral` final `rejected` insight_density_score `0.055`.

## Category Summary

- `high_integrity_viral` fixtures `2`, expected favored `2`, actual favored `0`, false positives `0`, false negatives `2`.
- `generic_viral_looking` fixtures `2`, expected favored `0`, actual favored `0`, false positives `0`, false negatives `0`.
- `manipulative_clickbait` fixtures `2`, expected favored `0`, actual favored `0`, false positives `0`, false negatives `0`.
- `outrage_bait` fixtures `2`, expected favored `0`, actual favored `0`, false positives `0`, false negatives `0`.
- `strong_but_nonviral` fixtures `2`, expected favored `0`, actual favored `0`, false positives `0`, false negatives `0`.
