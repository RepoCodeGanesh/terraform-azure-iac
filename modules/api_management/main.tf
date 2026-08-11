resource "azurerm_api_management" "this" {
  name                 = var.name
  location             = var.location
  resource_group_name  = var.resource_group_name
  publisher_name       = var.publisher_name
  publisher_email      = var.publisher_email
  sku_name             = var.sku_name
  virtual_network_type = var.virtual_network_type
  public_ip_address_id = var.public_ip_address_id
  tags                 = var.tags
}
