# Misclassification Analysis

## Summary

- The current validator preserved some coarse gating behavior, but it failed the v2 objective because it cannot separate rhetorical recurrence types into distinct semantic classes.
- The dominant failure mode is representational, not merely threshold-based.

## Boundary Findings

- `refrain_like`: current logic can warn correctly when repeated phrasing is obvious, but it does not represent escalation as graph growth.
- `motif_recall`: current logic lacks motif nodes and recall edges, so distance-based recurrence is invisible as a justified structure.
- `dialogue_callback`: current logic cannot distinguish callback-plus-correction from simple repetition because dialogue act edges are not modeled.
- `clean_progression`: causal extension can sometimes pass, but only indirectly through low overlap rather than explicit cause/extend edges.
- `semantic_spin`: current logic can often warn or fail, but it cannot name the boundary between spin and total collapse.
- `collapse` with high lexical diversity remains difficult because proposition identity is not tracked beyond coarse surrogate signals.
- `legitimate_recurrence` in emotional circling remains unstable because emotional-state transitions are not graph objects yet.

## Why The Suite Is Adversarial

- Several fixtures intentionally minimize phrase repetition while preserving the same proposition, which defeats overlap-driven heuristics.
- Several fixtures intentionally repeat wording while changing narrative pressure, which should earn recurrence credit rather than collapse penalty.
- Dialogue and motif cases require typed nodes and edges that the current validator does not emit.

## Recommendation

- Promote SemanticRedundancyValidator v2 only after `redundancy_class` and the required idea-graph evidence fields are produced directly by runtime evaluation.
