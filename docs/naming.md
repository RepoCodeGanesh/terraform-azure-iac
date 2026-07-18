# Naming

Root names are built from:

```text
<resource_group_prefix>-<environment>-<workspace>
```

For storage account-style names, `locals.tf` lowercases the value, removes hyphens, truncates to 21 characters, and appends a 3-character MD5 suffix when the raw value would exceed Azure's 24-character storage account limit.
