# staticwebapi

Deploys a simple Azure Static Web App wrapper for dev learning.

Registry module:

- Source: `Azure/avm-res-web-staticsite/azurerm`
- Version: `0.6.2`

The module exposes a common output contract used by the root pipeline automation. Azure Static Web Apps expose `primary_endpoint`; non-applicable outputs are returned as empty maps or `null`.
