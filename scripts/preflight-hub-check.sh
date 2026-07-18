#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<USAGE
Usage: $0 --subscription <id> --hub-rg <name> --storage <name> --container <name> [--keyvault <name>]
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

[ -n "${SUBSCRIPTION}" ] && [ -n "${HUB_RG}" ] && [ -n "${STORAGE}" ] || usage

command -v az >/dev/null 2>&1 || { echo "Azure CLI is required." >&2; exit 1; }

echo "Using subscription ${SUBSCRIPTION}."
az account set --subscription "${SUBSCRIPTION}"

echo "Checking hub resource group ${HUB_RG}."
if ! hub_rg_id=$(az group show --name "${HUB_RG}" --query id -o tsv); then
  echo "Hub resource group was not found or the identity cannot read it: ${HUB_RG}" >&2
  exit 1
fi
echo "Found hub resource group: ${hub_rg_id}"

echo "Checking hub storage account ${STORAGE}."
if ! storage_id=$(az storage account show --resource-group "${HUB_RG}" --name "${STORAGE}" --query id -o tsv); then
  echo "Storage account was not found in ${HUB_RG} or the identity cannot read it: ${STORAGE}" >&2
  exit 1
fi
echo "Found storage account: ${storage_id}"

if [ -n "${KEYVAULT}" ]; then
  echo "Checking optional hub Key Vault ${KEYVAULT}."
  if ! keyvault_id=$(az keyvault show --resource-group "${HUB_RG}" --name "${KEYVAULT}" --query id -o tsv); then
    echo "Key Vault was not found in ${HUB_RG} or the identity cannot read it: ${KEYVAULT}" >&2
    exit 1
  fi
  echo "Found Key Vault: ${keyvault_id}"
else
  echo "Skipping Key Vault check because --keyvault was not provided."
fi

echo "Checking backend container ${CONTAINER} in ${STORAGE}."
if ! container_exists=$(az storage container exists \
  --account-name "${STORAGE}" \
  --name "${CONTAINER}" \
  --auth-mode login \
  --query exists -o tsv); then
  echo "Could not check container ${CONTAINER}. Grant Storage Blob Data Reader or Storage Blob Data Contributor on ${STORAGE}." >&2
  exit 1
fi

if [ "${container_exists}" != "true" ]; then
  echo "Container ${CONTAINER} was not found in storage account ${STORAGE}." >&2
  exit 1
fi

echo "Preflight checks passed for dev hub ${HUB_RG}."
