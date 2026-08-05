locals {

  hyphen_name = lower(join("-", [
    var.resource_type,
    var.project,
    var.workload,
    var.environment,
    var.location_short,
    var.instance
  ]))

  compact_name = lower(join("", [
    var.resource_type,
    var.project,
    var.workload,
    var.environment,
    var.location_short,
    var.instance
  ]))

  compact_resource_types = [
    "st",
    "acr"
  ]

  resource_name = contains(local.compact_resource_types, var.resource_type) ? local.compact_name : local.hyphen_name
}