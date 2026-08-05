# Terraform Naming Module

## Purpose

Generates Azure resource names using the organization's naming convention.

## Naming Standard

```
<resource-type>-<project>-<workload>-<environment>-<location>-<instance>
```

Where:

- resource-type : Azure resource prefix
- project       : Project code
- workload      : boot, hub, shared, app, etc.
- environment   : d (Development), p (Production)
- location      : Azure region short code
- instance      : Instance number

## Examples

Hyphenated resources

```
kv-ht-boot-p-cin-01
rg-ht-hub-d-cin-01
vnet-ht-app-p-cin-01
```

Compact resources

```
sthtbootpcin01
acrhtshareddcin01
```

## Inputs

| Variable | Example |
|----------|---------|
| resource_type | kv |
| project | ht |
| workload_name | boot |
| environment | p |
| location_short | cin |
| instance | 01 |

## Output

| Output | Description |
|--------|-------------|
| name | Generated Azure resource name |

## Example

```hcl
module "bootstrap_kv_name" {

  source = "../../modules/naming"

  resource_type = "kv"

  project        = "ht"
  workload_name  = "boot"
  environment    = "p"
  location_short = "cin"
  instance       = "01"
}
```

Output

```
kv-ht-boot-p-cin-01
```