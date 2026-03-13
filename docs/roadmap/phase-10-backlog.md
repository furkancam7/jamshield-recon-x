# Phase 10 - Tactical Summary Backlog

## Goal

Convert mission, trust, and EW outputs into an operator-facing tactical summary without changing runtime autonomy authority.

## Scope

- Add deterministic tactical summary generation under `src/tactical_summary/`.
- Produce per-scenario `*_tactical_summary.json` artifacts.
- Produce run-level `tactical_summary_bundle.json`, `tactical_summary_bundle.md`, and `tactical_summary_bundle.csv`.
- Upgrade evaluation report and summary schema to `2.3`.
- Keep current evaluation summary artifacts separate from tactical artifacts.

## Contract Decisions

- Tactical output remains deterministic and template-based.
- No LLM or free-form generation is allowed in this phase.
- Canonical tactical reason and advisory codes are `snake_case`.
- `/mission/health` remains an architecture contract but is deferred in the current executable slice.

## Inputs

- `mission_state`
- `mission_primary_reason_code`
- `mission_confidence`
- `localization_mode`
- `effective_vio_state`
- `trust_primary_reason_code`
- `ew_risk_level`
- `ew_primary_reason_code`
- `ew_corridor_cost`
- `ew_affected_cell_count`

## Outputs

- Per-scenario tactical summary artifact
- Run-level tactical summary bundle
- Report fields:
  - `tactical_primary_reason_code`
  - `tactical_reason_codes`
  - `tactical_advisory_code`
  - `tactical_advisory_text`
  - `tactical_summary_text`
  - `tactical_summary_path`

## Verification Targets

- Unit tests for mapping precedence and deterministic template text
- Schema validation for tactical summary artifacts and bundle
- Regression checks for advisory coverage and runtime consistency
- Full baseline run over `s1-s20`

## Non-Goals

- Changing mission continuity state authority
- Feeding tactical outputs back into runtime autonomy
- Implementing `health_monitor_node`
- Replacing evaluation `summary.json/.md`
