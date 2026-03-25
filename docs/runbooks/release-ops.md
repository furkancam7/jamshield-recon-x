# Release Ops

## Purpose

This runbook defines the minimum release evidence package and decision policy for the simulation slice.

It standardizes release notes, checklist gating, and rollback decisions without changing runtime contracts.

## Release Evidence Template

Use this template for each candidate release.

```md
# Release Candidate

- release_id: <string>
- release_date_utc: <YYYY-MM-DD>
- target_branch: <main|prod>
- target_commit: <git_sha>
- prepared_by: <name>
- verified_by: <name>

## Contract References

- config_id baseline: <config_id>
- report schema version: <version>
- summary schema version: <version>

## Mandatory Evidence Links

- CI minimum gate (main/prod): <actions_run_url>
- CI full-matrix run (workflow_dispatch or schedule): <actions_run_url>
- unit test log or run evidence: <url_or_artifact_path>
- regression run directory: artifacts/runs/<run_id>
- artifact checker output: <url_or_artifact_path>

## Optional Gate Evidence

- launch probe gate: <url_or_artifact_path>
- verification probe gate: <url_or_artifact_path>
- health-monitor probe gate: <url_or_artifact_path>

## Decision

- verdict: <PASS|FAIL|INVALID>
- blocker_issue: <issue_url_or_none>
- notes: <short rationale>
```

## Release Checklist

1. Record release metadata (`release_id`, target commit, signer names).
2. Confirm CI minimum gate passed on the target branch.
3. Confirm a full-matrix workflow run exists for the candidate window.
4. Run and store unit test evidence (`python -m unittest discover -s tests/unit`).
5. Run and store baseline regression evidence (`bash scripts/run_regression.sh <run_id>`).
6. Run artifact checker and store result (`bash scripts/check_artifacts.sh artifacts/runs/<run_id>`).
7. Attach optional gate evidence when launch/verification/health probes are part of the candidate.
8. Resolve or link all blockers before sign-off.
9. Record final release verdict with explicit PASS/FAIL/INVALID.

## Decision Policy

### PASS

- Conditions:
  - CI minimum gate is green.
  - Full-matrix evidence exists and does not contain unresolved blockers.
  - Regression and artifact checks pass.
- Action:
  - Approve candidate and publish release note entry.

### FAIL

- Conditions:
  - Replay/evaluation is valid, but one or more acceptance or gate checks fail.
- Action:
  - Do not promote release.
  - Open or update blocker issue with failing checks and evidence links.
  - Re-run from the same target commit after fix.

### INVALID

- Conditions:
  - Missing/incomplete evidence bundle, hash mismatch, or deterministic replay divergence.
- Action:
  - Do not promote release.
  - Classify as integrity failure, log first divergence/missing artifact, and reopen validation from clean run artifacts.

## Sign-Off Rule

- A candidate is releasable only when the checklist is complete and verdict is `PASS`.
- Any `FAIL` or `INVALID` verdict requires blocker issue linkage before retry.
