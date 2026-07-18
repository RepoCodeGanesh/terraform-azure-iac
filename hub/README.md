# Dev Hub

The root module reads the existing dev hub resource group and storage account as data sources. Key Vault is optional. It creates the hub VNet `ht-cind-dev-vnet-hub-01` in the existing hub resource group and peers it to the spoke VNet.

Expected existing resources:

- Resource group: `ht-cind-dev-rg-hub-01`
- Storage account: `htcinddevsahub02`
- Blob container: `tfstate`
- Optional Key Vault: `ht-cind-dev-kv-hub-02`

Created by Terraform:

- Virtual network: `ht-cind-dev-vnet-hub-01`
- Address space: `10.41.0.0/16`

Run `../scripts/preflight-hub-check.sh` before planning in CI or locally.
