# provider.tf
provider "azurerm" {
  features {}
    # Ajoutez subscription_id pour spécifier explicitement la souscription
  subscription_id = var.subscription_id
  version = ">= 2.36.0"  # Vérifiez la dernière version disponible
}
