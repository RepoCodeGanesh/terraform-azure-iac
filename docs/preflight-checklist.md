# Preflight Checklist

Before running Terraform:

- Confirm the Azure DevOps service connection `dev` can access subscription `859a785c-bd38-402d-b595-1f44f40fb9bf` and is authorized for this pipeline.
- Confirm resource group `ht-cind-dev-rg-hub-01` exists.
- Confirm storage account `htcinddevsahub02` exists.
- Confirm blob container `tfstate` exists.
- Confirm Key Vault `ht-cind-dev-kv-hub-02` exists.
- Confirm the hub VNet name in `examples/dev/terraform.tfvars` matches the real dev hub VNet.

Run:

```bash
bash scripts/preflight-hub-check.sh \
  --subscription 859a785c-bd38-402d-b595-1f44f40fb9bf \
  --hub-rg ht-cind-dev-rg-hub-01 \
  --storage htcinddevsahub02 \
  --container tfstate \
  --keyvault ht-cind-dev-kv-hub-02
```
