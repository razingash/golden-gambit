terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

variable "backend_namespace" {
  description = "Namespace for the backend services"
  type        = string
}