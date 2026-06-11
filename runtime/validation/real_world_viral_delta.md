# Real-World Viral Delta

## Baseline

Before v6.2, all five real-world viral proxies failed `InsightDensityValidator`.

## After v6.2

### Reduced false negatives

#### Binge Drinking Warning Essay Proxy

- before insight_density_score: `0.12`
- after insight_density_score: `0.68`
- before insight validator status: `fail`
- after insight validator status: `warn`
- before final_status: `rejected`
- after final_status: `accepted_with_warnings`

#### Marina Keegan Farewell Proxy

- before insight_density_score: `0.04`
- after insight_density_score: `0.54`
- before insight validator status: `fail`
- after insight validator status: `warn`
- before final_status: `rejected`
- after final_status: `rejected`

Interpretation:
The insight layer now recognizes essayistic meaning, but the current v6 stack still blocks on other viral-growth validators.

#### Climate Letter Proxy

- before insight_density_score: `0.0`
- after insight_density_score: `0.371`
- before insight validator status: `fail`
- after insight validator status: `fail`

Interpretation:
Improved, but still below the warning floor. This remains a useful edge case for later tuning.

## Cases That Remained Strict

### Ayana Johnson Commencement Proxy

- before insight_density_score: `0.04`
- after insight_density_score: `0.053`
- insight validator status: `fail`

### Bee Rescue Viral Framing Proxy

- before insight_density_score: `0.12`
- after insight_density_score: `0.036`
- insight validator status: `fail`

Interpretation:
The system still rejects low-idea or thinly framed viral content. That is the intended behavior.

## Outcome

- real-world false negatives reduced: yes
- generic-motivation protection weakened: no
- clickbait protection weakened: no

The strongest gain is that meaningful, consequence-backed essayistic content is no longer automatically classified as empty insight.
