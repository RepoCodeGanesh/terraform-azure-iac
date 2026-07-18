#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --selected <all|module1,module2> [--modules-json <path>]" >&2
  exit 1
}

SELECTED=""
MODULES_JSON="modules.json"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selected) SELECTED="$2"; shift 2 ;;
    --modules-json) MODULES_JSON="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[ -n "${SELECTED}" ] || usage
[ -f "${MODULES_JSON}" ] || { echo "Module list not found: ${MODULES_JSON}" >&2; exit 1; }

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to validate module selections." >&2
  exit 1
fi

if [ "${SELECTED}" = "all" ]; then
  jq -r '.[]' "${MODULES_JSON}"
  exit 0
fi

printf '%s' "${SELECTED}" | tr ',' '\n' | sed '/^[[:space:]]*$/d' | while read -r module_name; do
  module_name="$(printf '%s' "${module_name}" | xargs)"
  if jq -e --arg module_name "${module_name}" 'index($module_name)' "${MODULES_JSON}" >/dev/null; then
    printf '%s\n' "${module_name}"
  else
    echo "Invalid module selection: ${module_name}" >&2
    echo "Available modules: $(jq -r 'join(",")' "${MODULES_JSON}")" >&2
    exit 2
  fi
done
