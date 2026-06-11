# V6 Viral Failure Analysis V2

- false_positives: 0
- false_negatives: 0

## v6_viral_integrity_fail_001
- expected_gating_outcome: rejected
- actual_gating_outcome: rejected
- viral_score: 0.306
- viral_integrity_score: 0.0
- manipulation_risk: 1.0
- clickbait_risk: 0.54
- diagnosis: Rejected because clickbait/manipulation signatures and low integrity remain incompatible with meaningful virality.
- clickbait_without_payoff: true
- emotional_manipulation: true
- identity_bait: true
- shallow_virality: false
- high_integrity_viral_cases: false

## v6_viral_integrity_pass_001
- expected_gating_outcome: accepted_with_warnings
- actual_gating_outcome: accepted_with_warnings
- viral_score: 0.447
- viral_integrity_score: 0.91
- manipulation_risk: 0.0
- clickbait_risk: 0.0
- diagnosis: Previously rejected because aggregate gating treated every low viral-growth subscore as blocking, even with strong integrity and low manipulation risk.
- clickbait_without_payoff: false
- emotional_manipulation: false
- identity_bait: false
- shallow_virality: false
- high_integrity_viral_cases: true
