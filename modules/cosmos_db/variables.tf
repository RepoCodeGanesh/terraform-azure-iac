variable "name" {
  description = "Name of the Cosmos DB account."
  type        = string
}

variable "location" {
  description = "Azure region for the Cosmos DB account."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name where Cosmos DB account will be created."
  type        = string
}

variable "enable_free_tier" {
  description = "Enable Cosmos DB Free Tier (1,000 RU/s + 25GB storage free per subscription)."
  type        = bool
  default     = true
}

variable "database_name" {
  description = "Name of the SQL Database."
  type        = string
  default     = "db-ai-assistant"
}

variable "container_name" {
  description = "Name of the SQL Container for chat history."
  type        = string
  default     = "chat_history"
}

variable "partition_key_path" {
  description = "Partition key path for the SQL Container."
  type        = string
  default     = "/sessionId"
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}
