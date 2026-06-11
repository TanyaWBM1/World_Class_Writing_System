# Phrase Diversity Rules v7.3

## Purpose

Prevent lazy repetition of phrases, rhetorical correction frames, grit expressions, sentence openings, and metaphor families while preserving intentional refrain and Tanya Lawson voice continuity.

## Hard Principles

- Do not flatten voice.
- Do not erase meaningful rhetorical recurrence.
- Block templated reuse, not purposeful rhythm.
- Allow refrain only when it deepens meaning, pressure, prayer, motif, or callback logic.

## Detection Targets

- exact phrase repetition
- near-duplicate phrase repetition
- repeated rhetorical correction frames
- repeated sentence openings
- overused metaphor domains
- overused grit phrases

## Generator Controls

- apply signature phrase cooldowns
- rotate metaphor domains across drafts
- cap grit opener reuse
- avoid repeating the same rhetorical correction frame in adjacent drafts

## Validator Interpretation

- `pass`: recurrence stays below cooldown thresholds or is explicitly justified as refrain-like
- `warn`: recurrence is noticeable but not yet templated
- `fail`: recurrence creates obvious template-dependence or phrase crutching
