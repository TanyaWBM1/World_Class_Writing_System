# V4 Hard Subversion Revolver Story Spec

## Purpose

Stress-test v4 long-range narrative intelligence against earned structural subversion that looks broken to literal setup/payoff heuristics.

## Core Benchmark Intent

The benchmark must appear to violate object-importance expectations while still satisfying narrative obligations through transformed payoff logic.

## Required Success Pattern

- Strong physical-object setup establishes a revolver as the obvious future instrument.
- Mid-story reinforcement increases confidence that the gun will be fired or displayed under threat.
- Expected literal payoff is withheld at the peak pressure point.
- The withheld payoff is not evasion.
- Object meaning transforms from tactical weapon to public evidence.
- Replacement payoff resolves:
  - external threat
  - character obligation
  - thematic obligation
- Character change is behavioral, not merely declarative.

## Validator Targeting

### SetupPayoffIntegrityValidator

- Must not flag `unmet_setup` merely because the revolver is not fired.
- Must detect transformed payoff linkage between:
  - revolver setup
  - hidden transfer record
  - public exposure of Vale
- Must score as structural success if payoff type changes but obligation remains fulfilled.

### ThreadPersistenceValidator

- Must track:
  - petitions threat
  - father's legacy
  - revolver meaning
  - Vale's coercive narrative
- Must see all high-importance threads as resolved by end state.

### CharacterArcConsistencyValidator

- Opening belief:
  - safety through secret control and defensive force
- End-state belief:
  - safety through public testimony and shared exposure
- Arc pass condition:
  - later behavior proves belief shift by refusing private possession and choosing public record.

### ThemeEvolutionValidator

- Motif/object transformation:
  - revolver as inherited protection myth
  - revolver as documentary proof of staged violence
- Theme should pass only if transformation is detected, not merely recurrence.

### PressureCurveValidator

- Pressure must rise through raid, apparent tactical choice, reveal, and public confrontation.
- Release must come through threat inversion rather than gunfire.

### SceneConsequenceValidator

- Scene 3 choice not to lift the gun must generate downstream state change.
- Scene 5 public exposure must alter room power dynamics.
- Scene 6 must demonstrate durable consequence through behavior and civic outcome.

## Special Signal Expectations

- `subversion_detected = true`
- `payoff_transformation_score >= 0.85`
- `earned_subversion_score >= 0.85`
- `belief_shift_detected = true`
- `object_function_transformed = true`

## False-Positive Failure Modes To Guard Against

- Literal-object-payoff bias:
  - assumes the revolver must be fired
- Tactical-resolution bias:
  - assumes visible threat display is the only meaningful payoff
- Declaration bias:
  - assumes arc only counts if the character states the new belief directly
- Motif-static bias:
  - misses functional transformation because the same object persists

## Expected Runtime Outcome

- V4 validator statuses:
  - `CharacterArcConsistencyValidator = pass`
  - `ThreadPersistenceValidator = pass`
  - `SetupPayoffIntegrityValidator = pass`
  - `ThemeEvolutionValidator = pass`
  - `PressureCurveValidator = pass`
  - `SceneConsequenceValidator = pass`
- Expected gating:
  - `accepted_with_warnings`

## Determinism Notes

- No external references required.
- All structural proof is contained in the text.
- Success depends on obligation interpretation, not subjective taste.
