output "id" {
  description = "Cosmos DB Account ID."
  value       = azurerm_cosmosdb_account.this.id
}

output "name" {
  description = "Cosmos DB Account name."
  value       = azurerm_cosmosdb_account.this.name
}

output "endpoint" {
  description = "Cosmos DB Account primary endpoint."
  value       = azurerm_cosmosdb_account.this.endpoint
}

output "primary_key" {
  description = "Cosmos DB Account primary key."
  value       = azurerm_cosmosdb_account.this.primary_key
  sensitive   = true
}

output "database_name" {
  description = "Cosmos DB SQL Database name."
  value       = azurerm_cosmosdb_sql_database.this.name
}

output "container_name" {
  description = "Cosmos DB SQL Container name."
  value       = azurerm_cosmosdb_sql_container.this.name
}
