# Dev Hub Lookups

The root module reads the existing dev hub as data sources. It does not create or modify hub resources except for the hub-to-spoke VNet peering.

Expected existing resources:

- Resource group: `ht-cind-dev-rg-hub-01`
- Virtual network: `ht-cind-dev-vnet-hub-01`
- Storage account: `htcinddevsahub02`
- Blob container: `tfstate`
- Key Vault: `ht-cind-dev-kv-hub-02`

Run `../scripts/preflight-hub-check.sh` before planning in CI or locally.
