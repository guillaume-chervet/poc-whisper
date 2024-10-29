# variables.tf
variable "resource_group_name" {
  type    = string
  default = "aks-resource-group"
}

variable "aks_cluster_name" {
  type    = string
  default = "aks-cluster"
}

variable "location" {
  type    = string
  default = "West Europe"
}

variable "subscription_id" {
  type = string
}

# Configuration du pool de nœuds
variable "node_min_count" {
  type    = number
  default = 1  # Nombre minimal de nœuds dans le pool
}

variable "node_max_count" {
  type    = number
  default = 5  # Nombre maximal de nœuds dans le pool
}
