# Backend Init

Terraform backend blocks cannot use variables. Keep `backend.tf` empty and pass the dev hub backend values during `terraform init`.

```bash
terraform init \
  -backend-config="resource_group_name=ht-cind-dev-rg-hub-01" \
  -backend-config="storage_account_name=htcinddevsahub02" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=cindia-dev-root.tfstate" \
  -backend-config="use_azuread_auth=true"
```
