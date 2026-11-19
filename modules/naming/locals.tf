locals {
  compact_resource_types = [
    "st",
    "acr"
  ]

  # Support both legacy single resource_type and modern batch resource_types
  types_to_process = distinct(compact(concat(
    var.resource_type != null ? [var.resource_type] : [],
    var.resource_types
  )))

  names = {
    for rt in local.types_to_process : rt => (
      contains(local.compact_resource_types, rt) ?
      lower(join("", [rt, var.project, var.workload, var.environment, var.location_short, var.instance])) :
      lower(join("-", [rt, var.project, var.workload, var.environment, var.location_short, var.instance]))
    )
  }

  resource_name = var.resource_type != null ? try(local.names[var.resource_type], "") : (
    length(local.names) > 0 ? values(local.names)[0] : ""
  )
}