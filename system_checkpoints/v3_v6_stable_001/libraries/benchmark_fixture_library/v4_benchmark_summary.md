# V4 Benchmark Summary

## Added Suites

- `character_arc_suite`
- `thread_persistence_suite`
- `setup_payoff_suite`

## Coverage

- Each suite contains `pass`, `warn`, `fail`, and `adversarial` fixtures.
- All fixtures are multi-paragraph and document-level by construction.
- The pack stresses state transitions across scenes rather than local sentence quality.

## Focus Areas

- Character growth continuity versus unsupported arc jumps
- Open-thread maintenance versus thread dropout masking
- Setup/payoff proportion, unpaid setups, and unsupported payoff reveals

## Determinism

- No external APIs
- Fixed passage text
- Explicit expected validator outcomes and gating outcomes
