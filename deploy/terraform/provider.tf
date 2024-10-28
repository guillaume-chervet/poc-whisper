# provider.tf
provider "azurerm" {
  features {}
    # Ajoutez subscription_id pour spécifier explicitement la souscription
  subscription_id = var.subscription_id
}
