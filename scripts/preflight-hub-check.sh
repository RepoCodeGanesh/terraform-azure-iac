#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<USAGE
Usage: $0 --subscription <id> --hub-rg <name> --storage <name> --container <name> --keyvault <name>
USAGE
  exit 1
}

SUBSCRIPTION=""
HUB_RG=""
STORAGE=""
CONTAINER="tfstate"
KEYVAULT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --subscription) SUBSCRIPTION="$2"; shift 2 ;;
    --hub-rg) HUB_RG="$2"; shift 2 ;;
    --storage) STORAGE="$2"; shift 2 ;;
    --container) CONTAINER="$2"; shift 2 ;;
    --keyvault) KEYVAULT="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; usage ;;
  esac
done

[ -n "${SUBSCRIPTION}" ] && [ -n "${HUB_RG}" ] && [ -n "${STORAGE}" ] && [ -n "${KEYVAULT}" ] || usage

command -v az >/dev/null 2>&1 || { echo "Azure CLI is required." >&2; exit 1; }

az account set --subscription "${SUBSCRIPTION}"
az group show --name "${HUB_RG}" --query id -o tsv >/dev/null
az storage account show --resource-group "${HUB_RG}" --name "${STORAGE}" --query id -o tsv >/dev/null
az keyvault show --resource-group "${HUB_RG}" --name "${KEYVAULT}" --query id -o tsv >/dev/null

az storage container exists \
  --account-name "${STORAGE}" \
  --name "${CONTAINER}" \
  --auth-mode login \
  --query exists -o tsv | grep -qi true

echo "Preflight checks passed for dev hub ${HUB_RG}."
