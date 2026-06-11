# Lexical Grounding Audit

- Date: `2026-03-21`
- Voice: `tanya_lawson_v1`

## Governed Files

- `live_word_blacklist.json`
- `rewrite_map_tanya_lawson.json`
- `lexical_edit_log.json`

## Current Seed Terms

- `friction`: `discourage`
- `lands`: `discourage`
- `leverage`: `block`
- `pressure`: `context_only`

## Runtime Behavior

- Lexical grounding now reads the live blacklist and rewrite map during generation.
- `discourage` terms are deterministically rewritten to the first preferred alternative.
- `block` terms are rewritten when possible and removed only if no allowed context or mapped rewrite exists.
- `context_only` terms are preserved when the surrounding context explicitly supports them.

## Validator Behavior

- Flags blacklisted terms with `status`, `reason`, and `suggested_rewrites`.
- Respects `context_only` allowances.
- Preserves Tanya Lawson depth by targeting repeated drift rather than flattening nuance.
