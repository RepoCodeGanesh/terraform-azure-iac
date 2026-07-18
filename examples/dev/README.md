# Dev Example

Use this folder for the single supported development environment.

```bash
terraform plan -var-file=examples/dev/terraform.tfvars
```

For targeted learning deployments, prefer the script:

```bash
bash scripts/run-target.sh --target staticwebapi --action plan \
  --backend-rg ht-cind-dev-rg-hub-01 \
  --backend-account htcinddevsahub02 \
  --backend-container tfstate \
  --backend-key cindia-dev-root.tfstate
```
