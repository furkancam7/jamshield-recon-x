#!/usr/bin/env bash
set -euo pipefail

OWNER="furkancam7"
REPO="jamshield-recon-x"
PROJECT_TITLE="JamShield Recon-X Roadmap"

PHASES=(
  "P0 Architecture Lock"
  "P1 Executable Vertical Slice"
  "P2 Determinism and Regression"
  "P3 Config and Artifact Hardening"
  "P4 VIO Health Upgrade"
  "P5 Real VIO Metric Skeleton"
  "P6 Localization Fusion"
  "P7 Trust Engine Maturity"
  "P8 Mission Continuity V2"
  "P9 EW Risk Map"
  "P10 Tactical Summary"
  "P11 Replay and Evaluation Hardening"
  "P12 ROS2 Runtime Migration"
  "P13 Deployment and Ops Hardening"
  "P14 Hardware-Portability Layer"
  "P15 Field Transition Preparation"
)

echo "Creating project..."
PROJECT_NUM=$(gh project create \
  --owner "$OWNER" \
  --title "$PROJECT_TITLE" \
  --format json \
  --jq '.number')

echo "Project number: $PROJECT_NUM"

echo "Linking repository..."
gh project link "$PROJECT_NUM" --owner "$OWNER" --repo "$OWNER/$REPO"

echo "Creating labels..."
for phase in {0..15}; do
  gh label create "phase:$phase" --repo "$OWNER/$REPO" --color "5319e7" --description "Phase $phase work" 2>/dev/null || true
done

for label in epic feature task bug test doc agent-ready blocked architecture config artifacts evaluation fusion vio trust ew replay ros2 ops portability field; do
  gh label create "$label" --repo "$OWNER/$REPO" --color "1d76db" --description "$label" 2>/dev/null || true
done

echo "Creating epic issues..."
for title in "${PHASES[@]}"; do
  phase_num=$(echo "$title" | sed -E 's/^P([0-9]+).*/\1/')
  gh issue create \
    --repo "$OWNER/$REPO" \
    --title "$title" \
    --label "epic,phase:$phase_num" \
    --body "Epic for $title

## Objective
Define and complete the roadmap items for $title.

## Acceptance Criteria
- [ ] Phase scope is explicitly defined
- [ ] Child issues created
- [ ] Validation criteria defined
- [ ] Phase completion review completed
"
done

echo "Done. Open:"
echo "https://github.com/$OWNER/$REPO/projects"