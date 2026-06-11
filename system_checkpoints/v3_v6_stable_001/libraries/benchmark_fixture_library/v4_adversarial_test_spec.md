# V4 Adversarial Lantern Story Spec

## Purpose

Stress v4 long-range narrative validators with a surface-polished story that fails structurally rather than locally.

## Target Validators

- `CharacterArcConsistencyValidator`
- `ThreadPersistenceValidator`
- `SetupPayoffIntegrityValidator`
- `ThemeEvolutionValidator`
- `PressureCurveValidator`
- `SceneConsequenceValidator`

## Structural Attack Pattern

- The opening establishes a high-weight setup around the cracked blue lantern and missing docket.
- A morally loaded character decision is staged with explicit consequence expectations.
- The lantern motif recurs visually across later scenes but never changes meaning.
- A ledger appears as a pseudo-payoff that does not actually resolve the planted setup.
- The courier thread and missing docket thread remain unresolved.
- The narration claims Mara has changed, but enacted behavior shows arc stagnation.

## Why It Is Adversarial

- The prose remains coherent, atmospheric, and controlled.
- Scene-to-scene continuity feels superficially intact.
- Motif repetition can masquerade as thematic sophistication.
- The ledger reveal can masquerade as payoff closure.
- Character-growth language can disguise the absence of actual arc movement.

## Expected Validator Outcomes

- `CharacterArcConsistencyValidator`: `warn`
  Arc language exceeds enacted arc change.
- `ThreadPersistenceValidator`: `fail`
  Two major threads stall or disappear without recovery.
- `SetupPayoffIntegrityValidator`: `fail`
  Primary setup is underpaid and the apparent payoff is misaligned.
- `ThemeEvolutionValidator`: `warn`
  Recurrent imagery is present, but thematic meaning does not evolve enough.
- `PressureCurveValidator`: `warn`
  Pressure is gestured at repeatedly, but escalation and release are structurally soft.
- `SceneConsequenceValidator`: `fail`
  Mara's key decision does not alter later scenes in a meaningful way.

## Expected Failure Modes

- `character_arc_discontinuity_failure`
- `thread_dropout_failure`
- `unpaid_setup_failure`
- `unsupported_payoff_failure`
- `theme_stagnation_failure`
- `scene_consequence_failure`

## Expected Gating Outcome

- `rejected`

## Review Notes

- Failures should be detected at the document level, not through sentence-level style weakness.
- This fixture is intended to separate local prose quality from structural narrative intelligence.
