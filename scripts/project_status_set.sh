#!/usr/bin/env bash
set -euo pipefail

OWNER="$1"
PROJECT_NUMBER="$2"
ITEM_URL="$3"
STATUS_NAME="$4"

PROJECT_JSON=$(gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json)
PROJECT_ID=$(echo "$PROJECT_JSON" | jq -r '.id')

FIELDS_JSON=$(gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --format json)
STATUS_FIELD_ID=$(echo "$FIELDS_JSON" | jq -r '.fields[] | select(.name=="Status") | .id')
STATUS_OPTION_ID=$(echo "$FIELDS_JSON" | jq -r --arg NAME "$STATUS_NAME" '
  .fields[]
  | select(.name=="Status")
  | .options[]
  | select(.name==$NAME)
  | .id
')

ITEM_ID=$(gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$ITEM_URL" --format json | jq -r '.id')

gh project item-edit \
  --id "$ITEM_ID" \
  --project-id "$PROJECT_ID" \
  --field-id "$STATUS_FIELD_ID" \
  --single-select-option-id "$STATUS_OPTION_ID"