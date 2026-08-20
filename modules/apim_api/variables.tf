variable "apim_id" {
  description = "Resource ID of the API Management service."
  type        = string
}

variable "apim_name" {
  description = "Name of the API Management service."
  type        = string
}

variable "apim_resource_group_name" {
  description = "Resource Group containing the API Management service."
  type        = string
}

variable "backend_name" {
  description = "Identifier for the APIM backend."
  type        = string
}

variable "backend_protocol" {
  description = "Protocol of the backend (http, soap)."
  type        = string
  default     = "http"
}

variable "backend_url" {
  description = "Target service URL for the backend."
  type        = string
}

variable "backend_description" {
  description = "Description for the APIM backend."
  type        = string
  default     = "APIM Backend"
}

variable "api_name" {
  description = "Unique resource name for the API in APIM."
  type        = string
}

variable "display_name" {
  description = "Display name of the API."
  type        = string
}

variable "path" {
  description = "URL path suffix for this API in APIM (e.g. tax-advisor or bankc)."
  type        = string
}

variable "protocols" {
  description = "List of protocols (https, http)."
  type        = list(string)
  default     = ["https"]
}

variable "subscription_required" {
  description = "Whether a subscription key is required to access the API."
  type        = bool
  default     = false
}

variable "operations" {
  description = "Map of API operations (endpoints) to register."
  type = map(object({
    display_name = string
    method       = string
    url_template = string
    description  = optional(string)
  }))
  default = {}
}

variable "custom_policy_xml" {
  description = "Optional custom XML policy to apply to the API. If null, a standard CORS + backend forward policy is used."
  type        = string
  default     = null
}
