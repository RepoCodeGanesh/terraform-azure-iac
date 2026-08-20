output "id" {
  description = "The ID of the AKS Cluster."
  value       = azurerm_kubernetes_cluster.this.id
}

output "name" {
  description = "The Name of the AKS Cluster."
  value       = azurerm_kubernetes_cluster.this.name
}

output "oidc_issuer_url" {
  description = "The OIDC issuer URL for Workload Identity Federation."
  value       = azurerm_kubernetes_cluster.this.oidc_issuer_url
}

output "control_plane_identity_id" {
  description = "The Resource ID of the AKS Control Plane User-Assigned Managed Identity."
  value       = azurerm_user_assigned_identity.aks_control_plane.id
}

output "control_plane_identity_principal_id" {
  description = "The Principal ID of the AKS Control Plane Managed Identity."
  value       = azurerm_user_assigned_identity.aks_control_plane.principal_id
}

output "node_resource_group" {
  description = "The auto-generated Resource Group containing the AKS agent nodes."
  value       = azurerm_kubernetes_cluster.this.node_resource_group
}

output "kube_config_raw" {
  description = "Raw Kubernetes configuration to authenticate against the cluster."
  value       = azurerm_kubernetes_cluster.this.kube_config_raw
  sensitive   = true
}
