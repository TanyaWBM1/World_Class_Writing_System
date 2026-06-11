# Ingestion Summary

## Scope

- Pass type: research ingestion and normalization only
- Source files processed: 4
- Structured records created: 434

## Source Totals

- core_failure_modes_01.md: 142 records
- evaluation_methods_01.md: 101 records
- hidden_techniques_01.md: 85 records
- system_design_patterns_01.md: 106 records

## Item Type Totals

- ruleset: 71
- operator: 121
- failure_mode: 42
- test_case: 32
- library_entry: 168

## Duplicate And Overlap Analysis

- Exact duplicate groups across files: 2
- Overlap candidates across files: 1
- Ambiguous mapping conflicts: 266
- Missing library targets: 0
- Escalation candidates for @research-evolution-architect: 246

## Notable Merge Candidates

- RULE-1 <-> RULE-SD-1 | similarity=0.61 | merge_candidate=false

## Terminology And Mapping Risks

- RU-core_failure_modes_01-001: RULE_PROSE_CONCRETENESS_MIN -> abstraction_control_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-002: RULE_GENERIC_TEMPLATE_CAP -> failure_mode_library, evaluation_library
- RU-core_failure_modes_01-003: RULE_SPEAKER_STYLE_DISTANCE_MIN -> dialogue_behavior_library, failure_mode_library, evaluation_library, voice_library
- RU-core_failure_modes_01-004: RULE_DIALOGUE_ACT_DIVERSITY_MIN -> dialogue_behavior_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-005: RULE_SENTENCE_LENGTH_VAR_MIN -> cadence_library, failure_mode_library, evaluation_library, sentence_structure_library
- RU-core_failure_modes_01-006: RULE_SYNTAX_TEMPLATE_REPEAT_CAP -> cadence_library, failure_mode_library, evaluation_library, sentence_structure_library
- RU-core_failure_modes_01-007: RULE_SCENE_GOAL_REQUIRED -> continuity_state_library, failure_mode_library, evaluation_library, narrative_pressure_library
- RU-core_failure_modes_01-008: RULE_PROMISE_RESOLUTION_RATE -> continuity_state_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-009: RULE_ENTITY_INVARIANT_ENFORCED -> continuity_state_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-010: RULE_CONTINUITY_CONTRADICTION_CAP -> continuity_state_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-011: RULE_ABSTRACTION_RATIO_MAX -> abstraction_control_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-012: RULE_META_SENTENCE_RUN_CAP -> cadence_library, abstraction_control_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-013: RULE_SEMANTIC_REDUNDANCY_CAP -> abstraction_control_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-014: RULE_SECTION_NOVELTY_MIN -> abstraction_control_library, failure_mode_library, evaluation_library
- RU-core_failure_modes_01-015: RULE_AFFECT_VARIANCE_MIN -> failure_mode_library, evaluation_library

## Escalate To @research-evolution-architect

- RU-core_failure_modes_01-001: RULE_PROSE_CONCRETENESS_MIN (core_failure_modes_01.md)
- RU-core_failure_modes_01-003: RULE_SPEAKER_STYLE_DISTANCE_MIN (core_failure_modes_01.md)
- RU-core_failure_modes_01-004: RULE_DIALOGUE_ACT_DIVERSITY_MIN (core_failure_modes_01.md)
- RU-core_failure_modes_01-005: RULE_SENTENCE_LENGTH_VAR_MIN (core_failure_modes_01.md)
- RU-core_failure_modes_01-006: RULE_SYNTAX_TEMPLATE_REPEAT_CAP (core_failure_modes_01.md)
- RU-core_failure_modes_01-007: RULE_SCENE_GOAL_REQUIRED (core_failure_modes_01.md)
- RU-core_failure_modes_01-008: RULE_PROMISE_RESOLUTION_RATE (core_failure_modes_01.md)
- RU-core_failure_modes_01-009: RULE_ENTITY_INVARIANT_ENFORCED (core_failure_modes_01.md)
- RU-core_failure_modes_01-010: RULE_CONTINUITY_CONTRADICTION_CAP (core_failure_modes_01.md)
- RU-core_failure_modes_01-011: RULE_ABSTRACTION_RATIO_MAX (core_failure_modes_01.md)
- RU-core_failure_modes_01-012: RULE_META_SENTENCE_RUN_CAP (core_failure_modes_01.md)
- RU-core_failure_modes_01-013: RULE_SEMANTIC_REDUNDANCY_CAP (core_failure_modes_01.md)
- RU-core_failure_modes_01-014: RULE_SECTION_NOVELTY_MIN (core_failure_modes_01.md)
- RU-core_failure_modes_01-017: RULE_CANON_NO_IMPLICIT_OVERRIDE (core_failure_modes_01.md)
- RU-core_failure_modes_01-018: RULE_TERM_DEFINITION_STABILITY (core_failure_modes_01.md)
- RU-core_failure_modes_01-019: RULE_STYLE_DISTANCE_MAX (core_failure_modes_01.md)
- RU-core_failure_modes_01-020: RULE_CORPUS_STYLE_DIVERSITY_MIN (core_failure_modes_01.md)
- RU-core_failure_modes_01-021: RULE_VOICE_DRIFT_CAP (core_failure_modes_01.md)
- RU-core_failure_modes_01-022: RULE_REVISION_SCOPE_STYLE_LOCK (core_failure_modes_01.md)
- RU-core_failure_modes_01-023: RULE_GENRE_BEAT_COVERAGE_MIN (core_failure_modes_01.md)

## Notes

- Source extracts were treated as source material, not live system truth.
- Original wording was preserved in `raw_text`; normalized forms were generated separately.
- Crosswalks are candidate mappings for downstream review, not production library commitments.