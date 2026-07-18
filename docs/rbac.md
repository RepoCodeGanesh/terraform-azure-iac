# RBAC

Use least privilege for the Azure DevOps service connection identity named `dev`:

- `Storage Blob Data Contributor` on storage account `htcinddevsahub02`.
- Optional: `Key Vault Reader` on Key Vault `ht-cind-dev-kv-hub-02` if `key_vault_name` is set.
- `Network Contributor` on the existing dev hub resource group if the pipeline creates hub-to-spoke peering.
- `Contributor` on the dev subscription or a narrower dev spoke scope for learning resources.

Avoid reading Key Vault secret values directly into Terraform unless required, because secret data can be stored in Terraform state.
