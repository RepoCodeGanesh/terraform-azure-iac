output "name" {
  description = "Private DNS zone name."
  value       = azurerm_private_dns_zone.this.name
}

output "id" {
  description = "Private DNS zone resource ID."
  value       = azurerm_private_dns_zone.this.id
}
