# Conflict Resolution Summary

## Resolution Policy

- Primary library: the existing normalized `candidate_library` from structured findings.
- Secondary libraries: every remaining `candidate_libraries` value preserved as a non-owning relationship.
- Deletions: none.

## Resolved Counts

- Rules: 71
- Validators: 121
- Failure modes: 42
- Multi-library conflicts resolved: 234

## Primary Ownership Totals

- abstraction_control_library: 13
- cadence_library: 32
- continuity_state_library: 20
- dialogue_behavior_library: 24
- evaluation_library: 40
- failure_mode_library: 57
- human_texture_library: 10
- narrative_pressure_library: 12
- system_design_library: 8
- voice_library: 18

## Secondary Relationship Totals

- abstraction_control_library: 4
- benchmark_fixture_library: 92
- cadence_library: 58
- continuity_state_library: 47
- dialogue_behavior_library: 6
- evaluation_library: 80
- failure_mode_library: 61
- genre_library: 5
- human_texture_library: 81
- idiosyncrasy_library: 15
- narrative_pressure_library: 4
- sentence_structure_library: 32
- system_design_library: 47
- voice_library: 23

## External Secondary Libraries

- human_texture_library: 81
- idiosyncrasy_library: 15
- narrative_pressure_library: 4
- sentence_structure_library: 32

## Sample Resolutions

- RU-core_failure_modes_01-001: primary=abstraction_control_library | secondary=failure_mode_library, evaluation_library
- RU-core_failure_modes_01-002: primary=failure_mode_library | secondary=evaluation_library
- RU-core_failure_modes_01-003: primary=dialogue_behavior_library | secondary=failure_mode_library, evaluation_library, voice_library
- RU-core_failure_modes_01-004: primary=dialogue_behavior_library | secondary=failure_mode_library, evaluation_library
- RU-core_failure_modes_01-005: primary=cadence_library | secondary=failure_mode_library, evaluation_library, sentence_structure_library
- FM-HT-1: primary=cadence_library | secondary=sentence_structure_library, system_design_library, benchmark_fixture_library
- FM-HT-10: primary=dialogue_behavior_library | secondary=human_texture_library, cadence_library
- FM-HT-11: primary=dialogue_behavior_library | secondary=human_texture_library, cadence_library
- FM-HT-12: primary=narrative_pressure_library | secondary=human_texture_library, cadence_library
- FM-HT-13: primary=dialogue_behavior_library | secondary=human_texture_library, cadence_library
- FM-1: primary=failure_mode_library | secondary=evaluation_library
- FM-1: primary=failure_mode_library | secondary=evaluation_library, benchmark_fixture_library
- FM-10: primary=failure_mode_library | secondary=evaluation_library, voice_library, human_texture_library
- FM-10: primary=failure_mode_library | secondary=voice_library, evaluation_library, benchmark_fixture_library
- FM-11: primary=failure_mode_library | secondary=evaluation_library, voice_library, human_texture_library

## Notes

- Existing library entries and relationship maps were preserved.
- Ownership was normalized without removing any cross-library associations.
- `sentence_structure_library` and `narrative_pressure_library` remain preserved as secondary relationships even though they are outside the currently structured library set.