#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="${REPO_ROOT}/apps"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to list deployment targets as JSON." >&2
  exit 1
fi

{
  echo "hub"
  if [ -d "${APP_DIR}" ]; then
    find "${APP_DIR}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n'
  fi
} | sort -u | jq -R -s -c 'split("\n")[:-1]'
