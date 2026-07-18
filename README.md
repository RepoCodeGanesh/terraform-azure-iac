# Dev Terraform Azure IaC

This is a simplified development-only Terraform repository for a hub-and-spoke learning environment. It connects a single spoke to the existing dev hub, stores state in the existing hub storage account, references the existing hub Key Vault, and deploys optional app modules through Azure DevOps.

## Dev Hub Values

| Setting | Value |
| --- | --- |
| Subscription ID | `859a785c-bd38-402d-b595-1f44f40fb9bf` |
| Tenant ID | `4cef0d84-84d6-4ed0-8abe-773b015bcf99` |
| Hub resource group | `ht-cind-dev-rg-hub-01` |
| Hub Key Vault | `ht-cind-dev-kv-hub-02` |
| Hub storage account | `htcinddevsahub02` |
| Backend container | `tfstate` |
| Naming prefix | `ht-cind` |
| Environment | `dev` |

## Layout

```text
.
├── ci/
├── docs/
├── examples/dev/
├── hub/
├── apps/
│   ├── securems/
│   ├── serverless/
│   └── staticwebapi/
└── scripts/
```

## Local Usage

```bash
bash scripts/preflight-hub-check.sh \
  --subscription 859a785c-bd38-402d-b595-1f44f40fb9bf \
  --hub-rg ht-cind-dev-rg-hub-01 \
  --storage htcinddevsahub02 \
  --container tfstate \
  --keyvault ht-cind-dev-kv-hub-02

terraform init \
  -backend-config="resource_group_name=ht-cind-dev-rg-hub-01" \
  -backend-config="storage_account_name=htcinddevsahub02" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=cindia-dev-root.tfstate" \
  -backend-config="use_azuread_auth=true"

terraform plan -var-file=examples/dev/terraform.tfvars
```

## Deployment Selection

Azure DevOps cannot dynamically populate a YAML parameter dropdown from repository folders during the same run. The CD pipeline therefore uses a queue-time variable and validates it against `hub` plus the folders under `apps/`:

```text
SELECTED_TARGETS=all
SELECTED_TARGETS=hub
SELECTED_TARGETS=staticwebapi,serverless
```

The pipeline discovers `apps/*`, adds the reserved `hub` target, validates the requested targets, and then runs `scripts/run-target.sh` for each selected target. Each folder under `apps/` is a wrapper that calls pinned Terraform Registry modules.
