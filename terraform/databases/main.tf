terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

variable "backend_services_namespace" {
  description = "Namespace for the backend services"
  type        = string
}