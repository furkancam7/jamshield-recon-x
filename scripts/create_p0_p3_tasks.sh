#!/usr/bin/env bash
set -euo pipefail

OWNER="furkancam7"
REPO="jamshield-recon-x"

create_issue() {
  local title="$1"
  local labels="$2"
  local body="$3"

  gh issue create \
    --repo "$OWNER/$REPO" \
    --title "$title" \
    --label "$labels" \
    --body "$body"
}

create_issue "P0-T1 Terminology lock document" \
"task,doc,architecture,phase:0,agent-ready" \
"## Context
JamShield Recon-X Sim requires strict terminology consistency across architecture, evaluation, and implementation docs.

## Objective
Create or update a terminology lock document defining core system terms.

## Constraints
- Do not change runtime behavior
- Do not redefine mission authority boundaries
- Keep terms aligned with existing docs

## Files Likely Affected
- docs/architecture/
- docs/

## Acceptance Criteria
- [ ] terminology-lock document exists
- [ ] trust, confidence, decision, fallback, determinism, runtime, evaluation are defined
- [ ] ambiguous overlapping definitions are removed
- [ ] language is consistent with current architecture docs

## Validation
- Review all new definitions against existing system overview docs
- Confirm no contradiction with mission_continuity decision authority

## Agent Eligible
yes"

create_issue "P0-T2 Runtime vs evaluation boundary document" \
"task,doc,architecture,evaluation,phase:0,agent-ready" \
"## Context
Ground truth must remain evaluation-only and must never affect runtime autonomy decisions.

## Objective
Document runtime versus evaluation boundaries.

## Constraints
- No code behavior changes required
- Must explicitly forbid runtime consumption of ground truth

## Files Likely Affected
- docs/architecture/
- docs/interfaces/

## Acceptance Criteria
- [ ] runtime-evaluation boundary document exists
- [ ] forbidden dependencies are listed
- [ ] evaluation-only data is explicitly named
- [ ] runtime-safe data is distinguished from evaluation-only data

## Validation
- Verify consistency with current docs and evaluation notes

## Agent Eligible
yes"

create_issue "P0-T3 Decision authority contract for mission_continuity" \
"task,doc,architecture,phase:0,agent-ready" \
"## Context
mission_continuity is the only decision authority in the system.

## Objective
Document the mission_continuity decision contract.

## Constraints
- trust_engine provides signals only
- no alternate decision path may be implied

## Files Likely Affected
- docs/interfaces/
- docs/architecture/

## Acceptance Criteria
- [ ] decision contract doc exists
- [ ] mission_continuity is explicitly defined as sole decision authority
- [ ] trust_engine is defined as signal provider only
- [ ] inputs and outputs are described clearly

## Validation
- Cross-check against architecture docs and current module names

## Agent Eligible
yes"

create_issue "P0-T4 Implementation status matrix" \
"task,doc,architecture,phase:0,agent-ready" \
"## Context
The documented target architecture is broader than the currently implemented repo surface.

## Objective
Add an implementation status matrix showing planned versus implemented modules.

## Constraints
- Must be honest
- Must not claim unimplemented modules are complete

## Files Likely Affected
- docs/architecture/implementation-status.md

## Acceptance Criteria
- [ ] status matrix exists
- [ ] major modules are listed
- [ ] each module is marked planned, partial, or implemented
- [ ] document reflects repo reality

## Validation
- Compare against current src/ and docs/ structure

## Agent Eligible
yes"

create_issue "P1-T1 Vertical slice execution path documentation" \
"task,doc,phase:1,agent-ready" \
"## Context
The repository already supports a baseline simulation execution path.

## Objective
Document the current executable vertical slice.

## Constraints
- Describe only current or clearly labeled partial behavior
- Do not invent missing runtime components

## Files Likely Affected
- docs/architecture/
- docs/runbooks/

## Acceptance Criteria
- [ ] vertical slice flow is documented
- [ ] entrypoints and scripts are listed
- [ ] baseline flow from scenario orchestration to artifacts is explained
- [ ] document matches current repo behavior

## Validation
- Verify with smoke test and existing scripts

## Agent Eligible
yes"

create_issue "P1-T2 Baseline scenario manifest validation" \
"task,test,phase:1,agent-ready" \
"## Context
Scenario manifests define reproducible simulation behavior and must be validated.

## Objective
Implement or strengthen manifest validation for baseline scenarios.

## Constraints
- Validation must be deterministic
- Must not rely on runtime ground truth

## Files Likely Affected
- scenarios/
- src/
- tests/

## Acceptance Criteria
- [ ] baseline manifest validation exists or is hardened
- [ ] missing required fields fail validation
- [ ] tests cover at least current baseline scenarios
- [ ] failure messages are readable

## Validation
- Run pytest for new validation tests

## Agent Eligible
yes"

create_issue "P1-T3 Smoke test contract hardening" \
"task,test,phase:1,agent-ready" \
"## Context
smoke_test.sh exists but its guarantees must be explicit.

## Objective
Define and harden the smoke test contract.

## Constraints
- Keep behavior lightweight
- Do not turn smoke test into full regression

## Files Likely Affected
- scripts/smoke_test.sh
- docs/
- tests/

## Acceptance Criteria
- [ ] smoke test guarantees are documented
- [ ] expected outputs are named
- [ ] deterministic assumptions are clarified
- [ ] failures are actionable

## Validation
- Run smoke test locally and verify documented expectations

## Agent Eligible
yes"

create_issue "P1-T4 Scenario report minimum required fields" \
"task,artifacts,test,phase:1,agent-ready" \
"## Context
Scenario reports must have a minimum stable structure.

## Objective
Define and enforce minimum required fields for scenario reports.

## Constraints
- Keep scope minimal
- Avoid introducing future-only schema fields

## Files Likely Affected
- src/evaluation/
- src/common/
- tests/

## Acceptance Criteria
- [ ] minimum required field set is defined
- [ ] report generation includes those fields
- [ ] invalid or incomplete report generation fails test
- [ ] documentation updated if needed

## Validation
- Run unit tests for scenario report generation

## Agent Eligible
yes"

create_issue "P2-T1 Deterministic seed policy" \
"task,doc,test,replay,phase:2,agent-ready" \
"## Context
Determinism must be enforced, not assumed.

## Objective
Define and implement deterministic seed policy.

## Constraints
- Must not introduce hidden randomness
- Policy must be compatible with current baseline scenarios

## Files Likely Affected
- docs/
- src/
- tests/

## Acceptance Criteria
- [ ] seed policy is documented
- [ ] deterministic default or explicit seed behavior is defined
- [ ] tests cover seed stability assumptions
- [ ] no undocumented random source remains in path under test

## Validation
- Run repeat test or unit tests covering seed behavior

## Agent Eligible
yes"

create_issue "P2-T2 Stable ordering rules for outputs" \
"task,test,artifacts,phase:2,agent-ready" \
"## Context
Artifacts must be canonically comparable across repeated runs.

## Objective
Implement stable ordering rules for outputs.

## Constraints
- Preserve semantics
- Do not rely on incidental Python dict behavior alone

## Files Likely Affected
- src/evaluation/
- src/common/
- tests/

## Acceptance Criteria
- [ ] canonical ordering policy is implemented
- [ ] output ordering is stable in comparable artifacts
- [ ] tests verify stability
- [ ] behavior is documented or self-evident in implementation

## Validation
- Re-run artifact generation and compare outputs

## Agent Eligible
yes"

create_issue "P2-T3 Regression baseline artifact comparison utility" \
"task,test,replay,phase:2,agent-ready" \
"## Context
Regression requires semantic comparison, not naive raw file comparison.

## Objective
Add canonical artifact comparison utilities.

## Constraints
- Ignore only truly non-semantic fields
- Diff output must help debugging

## Files Likely Affected
- src/evaluation/
- scripts/
- tests/

## Acceptance Criteria
- [ ] comparison utility exists
- [ ] ignore list is narrow and justified
- [ ] mismatches produce readable diff output
- [ ] tests cover compare behavior

## Validation
- Run tests with both matching and mismatching sample artifacts

## Agent Eligible
yes"

create_issue "P2-T4 Repeated baseline regression test" \
"task,test,replay,phase:2,agent-ready" \
"## Context
Deterministic behavior must be proven via repeated execution.

## Objective
Add a repeated-run regression test for baseline scenarios.

## Constraints
- Use existing baseline scenarios
- Keep runtime practical

## Files Likely Affected
- scripts/
- tests/
- src/

## Acceptance Criteria
- [ ] same baseline scenario is run multiple times
- [ ] comparable outputs are checked for equality
- [ ] test fails on semantic mismatch
- [ ] output explains mismatch clearly

## Validation
- Run repeated-run test locally

## Agent Eligible
yes"

create_issue "P2-T5 Regression runner contract documentation" \
"task,doc,replay,phase:2,agent-ready" \
"## Context
run_regression.sh exists but its contract should be explicit.

## Objective
Document regression runner inputs, outputs, and guarantees.

## Constraints
- Must reflect actual repo behavior
- Must not overstate coverage

## Files Likely Affected
- docs/
- scripts/run_regression.sh

## Acceptance Criteria
- [ ] regression runner contract doc exists
- [ ] inputs and produced artifacts are listed
- [ ] pass/fail meaning is explained
- [ ] relation to deterministic replay is documented

## Validation
- Cross-check against current regression script behavior

## Agent Eligible
yes"

create_issue "P3-T1 Typed configuration schema" \
"task,config,test,phase:3,agent-ready" \
"## Context
Phase 3 requires configuration-driven behavior with stable, typed config structures.

## Objective
Introduce typed configuration schema support.

## Constraints
- Must preserve deterministic behavior
- Keep config surface aligned with actual system modules

## Files Likely Affected
- src/common/
- configs/
- tests/unit/

## Acceptance Criteria
- [ ] typed config classes exist
- [ ] config sections are logically separated
- [ ] invalid config fails validation
- [ ] tests cover typed config loading

## Validation
- Run pytest for config-related tests
- Ensure smoke path still works

## Agent Eligible
yes"

create_issue "P3-T2 Config resolution precedence" \
"task,config,test,phase:3,agent-ready" \
"## Context
Effective config must be resolved deterministically.

## Objective
Implement base, scenario override, and CLI override precedence.

## Constraints
- Precedence must be explicit
- No hidden environment override behavior

## Files Likely Affected
- src/common/
- configs/
- tests/unit/

## Acceptance Criteria
- [ ] precedence order is implemented
- [ ] resolution logic is centralized
- [ ] tests verify precedence behavior
- [ ] effective config is deterministic

## Validation
- Run unit tests with override permutations

## Agent Eligible
yes"

create_issue "P3-T3 Canonical config serialization" \
"task,config,test,phase:3,agent-ready" \
"## Context
Stable config_id generation depends on canonical serialization.

## Objective
Implement canonical serialization for resolved config.

## Constraints
- Stable key ordering required
- Serialization must be deterministic

## Files Likely Affected
- src/common/
- tests/unit/

## Acceptance Criteria
- [ ] canonical serialization utility exists
- [ ] same effective config always yields same serialized content
- [ ] ordering is stable
- [ ] tests cover canonical behavior

## Validation
- Run serialization tests multiple times

## Agent Eligible
yes"

create_issue "P3-T4 config_id hashing" \
"task,config,test,phase:3,agent-ready" \
"## Context
Each run must carry a stable config_id.

## Objective
Generate config_id from canonical config content.

## Constraints
- Hash input must be canonicalized
- Same config must yield same config_id

## Files Likely Affected
- src/common/
- src/evaluation/
- tests/unit/

## Acceptance Criteria
- [ ] config_id generation exists
- [ ] stable hashing is used
- [ ] same effective config yields same id
- [ ] tests verify stability

## Validation
- Run config_id tests with repeated inputs

## Agent Eligible
yes"

create_issue "P3-T5 software_revision resolver" \
"task,artifacts,ops,test,phase:3,agent-ready" \
"## Context
Artifacts must include software provenance.

## Objective
Implement software_revision resolution.

## Constraints
- Prefer explicit revision, then CI env, then git SHA
- Fallback must be deterministic and visible

## Files Likely Affected
- src/common/
- src/evaluation/
- tests/

## Acceptance Criteria
- [ ] resolver exists
- [ ] priority order is implemented
- [ ] output can be attached to artifacts
- [ ] tests cover resolution behavior

## Validation
- Run tests with mocked inputs

## Agent Eligible
yes"

create_issue "P3-T6 Artifact metadata standardization" \
"task,artifacts,test,phase:3,agent-ready" \
"## Context
Artifacts currently need stronger provenance and versioning.

## Objective
Standardize required metadata in all core artifacts.

## Constraints
- Use fields already aligned with roadmap goals
- Avoid adding speculative future-only metadata

## Files Likely Affected
- src/evaluation/
- src/common/
- tests/

## Acceptance Criteria
- [ ] required metadata fields are defined
- [ ] scenario and summary artifacts include them
- [ ] tests fail for missing required metadata
- [ ] metadata is stable across repeated runs except explicitly non-semantic fields

## Validation
- Run artifact tests and inspect sample outputs

## Agent Eligible
yes"

create_issue "P3-T7 ScenarioReport schema model" \
"task,artifacts,test,phase:3,agent-ready" \
"## Context
Scenario reports need formal validation.

## Objective
Create a typed schema model for ScenarioReport.

## Constraints
- Keep schema aligned with current implemented outputs
- Include schema versioning

## Files Likely Affected
- src/evaluation/
- tests/

## Acceptance Criteria
- [ ] typed ScenarioReport model exists
- [ ] invalid payload fails validation
- [ ] schema version field exists
- [ ] tests cover valid and invalid cases

## Validation
- Run schema validation tests

## Agent Eligible
yes"

create_issue "P3-T8 RunSummary schema model" \
"task,artifacts,test,phase:3,agent-ready" \
"## Context
Run summary output must be machine-readable and stable.

## Objective
Create typed schema model for RunSummary.

## Constraints
- summary.json must remain authoritative
- model must reflect current use

## Files Likely Affected
- src/evaluation/
- tests/

## Acceptance Criteria
- [ ] typed RunSummary model exists
- [ ] invalid payload fails validation
- [ ] summary.json shape is formalized
- [ ] tests cover valid and invalid summary payloads

## Validation
- Run summary schema tests

## Agent Eligible
yes"

create_issue "P3-T9 RegressionSummary schema model" \
"task,artifacts,test,replay,phase:3,agent-ready" \
"## Context
Regression aggregation needs formal structure.

## Objective
Create typed schema model for RegressionSummary.

## Constraints
- Must support current regression output style
- Avoid over-design

## Files Likely Affected
- src/evaluation/
- tests/

## Acceptance Criteria
- [ ] typed RegressionSummary model exists
- [ ] invalid payload fails validation
- [ ] aggregate field structure is explicit
- [ ] tests cover regression summary validation

## Validation
- Run regression summary schema tests

## Agent Eligible
yes"

create_issue "P3-T10 Artifact validation layer" \
"task,artifacts,test,phase:3,agent-ready" \
"## Context
Schema must be enforced, not merely documented.

## Objective
Add artifact validation into generation and/or checking path.

## Constraints
- Validation errors must be readable
- Do not silently coerce bad payloads

## Files Likely Affected
- src/evaluation/
- src/common/
- tests/

## Acceptance Criteria
- [ ] validation layer exists
- [ ] invalid artifact generation path fails
- [ ] error messages are readable
- [ ] tests cover validation failure

## Validation
- Run tests with intentionally malformed payloads

## Agent Eligible
yes"

create_issue "P3-T11 Artifact checker upgrade" \
"task,artifacts,test,phase:3,agent-ready" \
"## Context
Artifact checking must validate contract, not just presence.

## Objective
Upgrade artifact checker to validate schema and required metadata.

## Constraints
- Keep CLI or script usage practical
- Preserve current baseline use where possible

## Files Likely Affected
- scripts/check_artifacts.sh
- src/
- tests/

## Acceptance Criteria
- [ ] artifact checker validates schema-aware structure
- [ ] missing required metadata fails
- [ ] malformed artifact fails
- [ ] tests cover checker behavior

## Validation
- Run checker against valid and invalid sample artifacts

## Agent Eligible
yes"

create_issue "P3-T12 summary.json authoritative and summary.md derived" \
"task,artifacts,test,phase:3,agent-ready" \
"## Context
Machine-readable summary must be the source of truth.

## Objective
Ensure summary.json is authoritative and summary.md is derived from it.

## Constraints
- Markdown must not become the contract source
- Derived rendering should be deterministic

## Files Likely Affected
- src/evaluation/
- tests/

## Acceptance Criteria
- [ ] summary.json is treated as source of truth
- [ ] summary.md is generated from summary.json
- [ ] deterministic rendering policy is applied
- [ ] tests or docs verify source-of-truth rule

## Validation
- Regenerate summaries and verify consistency

## Agent Eligible
yes"

create_issue "P3-T13 Repeated-run determinism harness" \
"task,test,replay,phase:3,agent-ready" \
"## Context
Repeated-run determinism is a mandatory system property.

## Objective
Implement a repeated-run determinism harness for baseline scenarios.

## Constraints
- Must compare semantic outputs, not raw timestamps
- Ignore list must remain narrow

## Files Likely Affected
- scripts/
- tests/
- src/evaluation/

## Acceptance Criteria
- [ ] repeated-run harness exists
- [ ] same scenario can be run multiple times
- [ ] comparable artifacts are checked for semantic equality
- [ ] mismatch diff is readable

## Validation
- Run harness locally for at least one baseline scenario

## Agent Eligible
yes"

create_issue "P3-T14 Artifact manifest generation" \
"task,artifacts,replay,test,phase:3,agent-ready" \
"## Context
Run outputs need lineage and file-level traceability.

## Objective
Generate an artifact manifest for produced run outputs.

## Constraints
- Keep manifest minimal but useful
- Include checksums and core metadata

## Files Likely Affected
- src/evaluation/
- src/common/
- tests/

## Acceptance Criteria
- [ ] manifest generation exists
- [ ] produced files are listed
- [ ] checksums are included
- [ ] tests cover manifest structure

## Validation
- Generate manifest from a baseline run and inspect result

## Agent Eligible
yes"

create_issue "P3-T15 Phase 3 contract documentation" \
"task,doc,config,artifacts,phase:3,agent-ready" \
"## Context
Phase 3 requires stable public internal contracts for config and artifacts.

## Objective
Document config and artifact contracts for Phase 3.

## Constraints
- Must reflect implementation reality
- Must not invent unsupported fields or flows

## Files Likely Affected
- docs/interfaces/

## Acceptance Criteria
- [ ] config contract document exists
- [ ] artifact contract document exists
- [ ] config_id derivation is documented
- [ ] required metadata fields are documented

## Validation
- Cross-check docs against implementation and tests

## Agent Eligible
yes"

echo "P0-P3 task issues created."