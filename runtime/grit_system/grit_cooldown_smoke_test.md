# Grit Cooldown Smoke Test

## Case 1: Reuse-Heavy Signature Phrase

- mode: `authority`
- requested_grit_level: `high`
- recent_grit_phrases:
  - `that is not confusion. it is avoidance dressed up as uncertainty.`
  - `that is not confusion. it is avoidance dressed up as uncertainty.`
- recent_grit_phrase_counts:
  - `that is not confusion. it is avoidance dressed up as uncertainty.`: `3`
- current_draft_grit_phrases:
  - `that is not confusion. it is avoidance dressed up as uncertainty.`

Expected behavior:
- cooldown applies
- overused high-grit phrase is penalized
- alternative high-grit phrase is selected

Observed behavior:
- `grit_cooldown_applied: true`
- selected phrase: `Stop pretending this is complexity when it is refusal.`
- cooled phrase: `That is not confusion. It is avoidance dressed up as uncertainty.`
- cooled phrase penalty: `1.148`

Result: pass

## Case 2: High Grit With Varied Phrasing

- mode: `authority`
- requested_grit_level: `high`
- recent_grit_phrases:
  - `you are going in circles, and some part of you already knows why.`
- recent_grit_phrase_counts:
  - `you are going in circles, and some part of you already knows why.`: `1`
- current_draft_grit_phrases: none

Expected behavior:
- no cooldown penalty against unrelated high-grit family
- high grit remains available
- selector remains deterministic

Observed behavior:
- `grit_cooldown_applied: false`
- selected phrase: `Stop pretending this is complexity when it is refusal.`
- high-grit family remained available without forced softening

Result: pass

## Integration Check

- `runtime/generation/v7_generator.py` executed successfully after selector changes.
- Grit phrase selection happens before the v7.3 phrase diversity layer.
- Existing phrase diversity outputs remain intact.

Overall result: pass
