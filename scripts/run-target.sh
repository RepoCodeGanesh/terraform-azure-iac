#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<USAGE
Usage: $0 --target <hub|app-name> --action <plan|apply> --backend-rg <resource-group> --backend-account <account> --backend-container <container> --backend-key <key> [--var-file <path>] [--plan-dir <path>]
USAGE
  exit 1
}

TARGET_NAME=""
ACTION=""
BACKEND_RG="ht-cind-dev-rg-hub-01"
BACKEND_ACCOUNT="htcinddevsahub02"
BACKEND_CONTAINER="tfstate"
BACKEND_KEY="cindia-dev-root.tfstate"
VAR_FILE="examples/dev/terraform.tfvars"
PLAN_DIR="tfplans"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target) TARGET_NAME="$2"; shift 2 ;;
    --action) ACTION="$2"; shift 2 ;;
    --backend-rg) BACKEND_RG="$2"; shift 2 ;;
    --backend-account) BACKEND_ACCOUNT="$2"; shift 2 ;;
    --backend-container) BACKEND_CONTAINER="$2"; shift 2 ;;
    --backend-key) BACKEND_KEY="$2"; shift 2 ;;
    --var-file) VAR_FILE="$2"; shift 2 ;;
    --plan-dir) PLAN_DIR="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[ -n "${TARGET_NAME}" ] || usage
[ "${ACTION}" = "plan" ] || [ "${ACTION}" = "apply" ] || usage

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

if [ "${TARGET_NAME}" != "hub" ] && [ ! -d "apps/${TARGET_NAME}" ]; then
  echo "Target not found. Expected 'hub' or a folder under apps/: ${TARGET_NAME}" >&2
  exit 2
fi

terraform init \
  -backend-config="resource_group_name=${BACKEND_RG}" \
  -backend-config="storage_account_name=${BACKEND_ACCOUNT}" \
  -backend-config="container_name=${BACKEND_CONTAINER}" \
  -backend-config="key=${BACKEND_KEY}" \
  -backend-config="use_azuread_auth=true"

if [ "${TARGET_NAME}" = "hub" ]; then
  TARGETS=(
    "-target=data.azurerm_resource_group.hub"
    "-target=data.azurerm_storage_account.hub_state"
    "-target=data.azurerm_key_vault.hub"
    "-target=azurerm_virtual_network.hub"
    "-target=azurerm_resource_group.spoke"
    "-target=azurerm_virtual_network.spoke"
    "-target=azurerm_subnet.spoke"
    "-target=azurerm_virtual_network_peering.spoke_to_hub"
    "-target=azurerm_virtual_network_peering.hub_to_spoke"
  )
else
  TARGETS=("-target=module.${TARGET_NAME}[\"${TARGET_NAME}\"]")
fi

if [ "${ACTION}" = "plan" ]; then
  mkdir -p "${PLAN_DIR}"
  terraform plan -var-file="${VAR_FILE}" "${TARGETS[@]}" -out="${PLAN_DIR}/${TARGET_NAME}.tfplan"
else
  if [ -f "${PLAN_DIR}/${TARGET_NAME}.tfplan" ]; then
    terraform apply -auto-approve "${PLAN_DIR}/${TARGET_NAME}.tfplan"
  else
    terraform apply -var-file="${VAR_FILE}" "${TARGETS[@]}" -auto-approve
  fi
  if [ "${TARGET_NAME}" != "hub" ]; then
    if terraform output -json module_outputs >"${PLAN_DIR}/${TARGET_NAME}-outputs.json" 2>/dev/null; then
      jq --arg target_name "${TARGET_NAME}" '.[$target_name]' "${PLAN_DIR}/${TARGET_NAME}-outputs.json"
    else
      echo "module_outputs is not available in state yet; apply completed successfully."
    fi
  fi
fi
