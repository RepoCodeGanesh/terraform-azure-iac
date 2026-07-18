#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --selected <all|hub|app1,app2> [--targets-json <path>]" >&2
  exit 1
}

SELECTED=""
TARGETS_JSON="deployment-targets.json"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selected) SELECTED="$2"; shift 2 ;;
    --targets-json) TARGETS_JSON="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[ -n "${SELECTED}" ] || usage
[ -f "${TARGETS_JSON}" ] || { echo "Target list not found: ${TARGETS_JSON}" >&2; exit 1; }

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to validate target selections." >&2
  exit 1
fi

if [ "${SELECTED}" = "all" ]; then
  jq -r '.[]' "${TARGETS_JSON}"
  exit 0
fi

printf '%s' "${SELECTED}" | tr ',' '\n' | sed '/^[[:space:]]*$/d' | while read -r target_name; do
  target_name="$(printf '%s' "${target_name}" | xargs)"
  if jq -e --arg target_name "${target_name}" 'index($target_name)' "${TARGETS_JSON}" >/dev/null; then
    printf '%s\n' "${target_name}"
  else
    echo "Invalid deployment target: ${target_name}" >&2
    echo "Available targets: $(jq -r 'join(",")' "${TARGETS_JSON}")" >&2
    exit 2
  fi
done
