#!/usr/bin/env bash
set -euo pipefail

OWNER="furkancam7"
REPO="jamshield-recon-x"
PROJECT_NUMBER="4"

for i in $(seq 1 16); do
  ISSUE_URL="https://github.com/$OWNER/$REPO/issues/$i"
  echo "Adding $ISSUE_URL"
  gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$ISSUE_URL"
done

echo "Done."