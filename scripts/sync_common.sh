#!/usr/bin/env bash
# Copies src/common/ into each Lambda package so SAM can build them independently.
# Run this from the repo root before `sam build`.

set -euo pipefail

COMMON_SRC="src/common"
HANDLERS=(create_ticket get_ticket list_tickets update_ticket delete_ticket)

for handler in "${HANDLERS[@]}"; do
  dest="src/${handler}/common"
  echo "Syncing ${COMMON_SRC} → ${dest}"
  rm -rf "${dest}"
  cp -r "${COMMON_SRC}" "${dest}"
done

echo "Done. Run: cd infra && sam build && sam deploy --guided"
