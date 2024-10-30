# main.tf
resource "azurerm_resource_group" "aks_rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  location            = var.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  dns_prefix          = "k8sdns"
  http_application_routing_enabled = true

  default_node_pool {
    name       = "default"
    vm_size    = "Standard_DS2_v2"
    auto_scaling_enabled = true       # Active l'autoscaling du pool de nœuds
    min_count          = var.node_min_count
    max_count          = var.node_max_count
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
  }

  tags = {
    environment = "testing"
  }
}
