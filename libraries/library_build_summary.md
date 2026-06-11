# Library Build Summary

## Libraries Created

- failure_mode_library
- abstraction_control_library
- dialogue_behavior_library
- cadence_library
- continuity_state_library
- evaluation_library
- benchmark_fixture_library
- voice_library
- genre_library
- system_design_library

## Entry Counts

- failure_mode_library: 16
- abstraction_control_library: 3
- dialogue_behavior_library: 3
- cadence_library: 3
- continuity_state_library: 3
- evaluation_library: 13
- benchmark_fixture_library: 12
- voice_library: 3
- genre_library: 3
- system_design_library: 7

## Major Linkages Established

- Rule to validator links: 60 rules mapped
- Failure mode to rule links: 33 failure modes mapped
- Validator to failure mode links: 46 validators mapped
- Techniques from hidden-techniques findings were linked into cadence, dialogue behavior, abstraction control, and voice-oriented enforcement opportunities where proposal evidence existed.

## Schema Integration

- evaluation outputs: metric family, config version, evidence spans, calibration references, stability metadata
- enforcement reports: rule id, threshold snapshot, violation spans, affected dimensions, recommended action
- narrative state tracking: entities, canon invariants, promises, threads, scene goals, pressure state, state diffs

## Benchmark Structure

- Fixtures are organized in `benchmark_fixture_library` entries by failure mode, evaluation type, and narrative dimension via `fixture_axes`.

## Unresolved Conflicts

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

## Missing Definitions

- No required library was left without at least one structured entry.