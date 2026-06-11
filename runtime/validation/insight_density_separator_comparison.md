# Insight Density Separator Comparison

## Cases

- High-integrity viral piece: `accepted_with_warnings`
- Generic viral-looking piece: `rejected`

## Core Separation

- insight_density_score: 0.66 vs 0.0
- abstraction_ratio: 0.5 vs 1.0
- concrete_example_count: 5 vs 0
- generic_motivation_detected: False vs True
- empty_insight_detected: False vs True
- shallow_philosophy_detected: False vs True

## Verdict

- InsightDensityValidator is the separating validator: True
- It is not the only differing signal, but it is the clearest value-layer discriminator between the two cases.
- The high-integrity case carries concrete support and avoids generic uplift language.
- The generic case uses portable motivation language without enough idea density to survive v6 gating.
