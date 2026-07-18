#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODULE_DIR="${REPO_ROOT}/modules"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to list modules as JSON." >&2
  exit 1
fi

if [ ! -d "${MODULE_DIR}" ]; then
  echo "[]" 
  exit 0
fi

find "${MODULE_DIR}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' \
  | sort \
  | jq -R -s -c 'split("\n")[:-1]'
