#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<USAGE
Usage: $0 --module <name> --action <plan|apply> --backend-rg <resource-group> --backend-account <account> --backend-container <container> --backend-key <key> [--var-file <path>]
USAGE
  exit 1
}

MODULE=""
ACTION=""
BACKEND_RG="ht-cind-dev-rg-hub-01"
BACKEND_ACCOUNT="htcinddevsahub02"
BACKEND_CONTAINER="tfstate"
BACKEND_KEY="cindia-dev-root.tfstate"
VAR_FILE="examples/dev/terraform.tfvars"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --module) MODULE="$2"; shift 2 ;;
    --action) ACTION="$2"; shift 2 ;;
    --backend-rg) BACKEND_RG="$2"; shift 2 ;;
    --backend-account) BACKEND_ACCOUNT="$2"; shift 2 ;;
    --backend-container) BACKEND_CONTAINER="$2"; shift 2 ;;
    --backend-key) BACKEND_KEY="$2"; shift 2 ;;
    --var-file) VAR_FILE="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[ -n "${MODULE}" ] || usage
[ "${ACTION}" = "plan" ] || [ "${ACTION}" = "apply" ] || usage

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

if [ ! -d "modules/${MODULE}" ]; then
  echo "Module folder not found: modules/${MODULE}" >&2
  exit 2
fi

terraform init \
  -backend-config="resource_group_name=${BACKEND_RG}" \
  -backend-config="storage_account_name=${BACKEND_ACCOUNT}" \
  -backend-config="container_name=${BACKEND_CONTAINER}" \
  -backend-config="key=${BACKEND_KEY}" \
  -backend-config="use_azuread_auth=true"

TARGET="module.${MODULE}[\"${MODULE}\"]"

if [ "${ACTION}" = "plan" ]; then
  terraform plan -var-file="${VAR_FILE}" -target="${TARGET}" -out="${MODULE}.tfplan"
else
  terraform apply -var-file="${VAR_FILE}" -target="${TARGET}" -auto-approve
  terraform output -json module_outputs | jq --arg module_name "${MODULE}" '.[$module_name]'
fi
