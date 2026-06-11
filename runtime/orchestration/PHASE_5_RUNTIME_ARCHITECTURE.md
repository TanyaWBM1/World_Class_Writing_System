# Phase 5 Runtime Architecture

## Purpose

Phase 5 is the first execution architecture layer for the World Class Writing System.

It accepts structured run inputs, resolves libraries and owned rules, performs a controlled draft-generation handoff, runs ordered quality passes, and emits authoritative evaluation and enforcement artifacts.

## Evaluation-First Gating

Final run states:
- `accepted`
- `accepted_with_warnings`
- `rejected`

Acceptance is determined only after:
1. prose enforcement pass
2. evaluation gate
3. artifact generation

## Authoritative Principles

- Enforcement is authoritative, not advisory.
- Continuity is evaluated by state and meaning, not by shallow text reuse.
- Cadence is a core quality dimension.
- Voice and genre are behavior systems, not surface ornament.
- No run may mutate live runtime rules, validators, or libraries.
- Every run emits structured artifacts even when rejected.

## Run Artifact Bundle

Each run must emit:
- `input_bundle.json`
- `resolved_libraries.json`
- `draft_output.txt`
- `evaluation_report.json`
- `enforcement_report.json`
- `failure_map.json`
- `run_summary.json`
