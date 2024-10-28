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
  default = "East US"
}

variable "subscription_id" {
  type = string
}