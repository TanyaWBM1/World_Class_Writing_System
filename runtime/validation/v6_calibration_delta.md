# V6 Calibration Delta

## Accounting correction
- previous false_positives: 0
- previous false_negatives: 0
- corrected false_positives: 0
- corrected false_negatives: 0

## Pass-case rejection diagnosis
- Fixture `v6_viral_integrity_pass_001` originally failed because the general aggregation logic treated every low viral-growth subscore as blocking and never emitted a high-integrity viral exception.
- The calibrated path now permits `accepted_with_warnings` when integrity is strong, risks are low, viral_score is mid-band, and no v4 narrative failure is present.

## Outcome changes
- v6_viral_integrity_fail_001: gating rejected -> rejected; viral_score 0.231 -> 0.306; viral_integrity_score 0.0 -> 0.0
- v6_viral_integrity_pass_001: gating rejected -> accepted_with_warnings; viral_score 0.362 -> 0.447; viral_integrity_score 0.91 -> 0.91