terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

variable "frontend_namespace" {
  description = "Namespace for the frontend services"
  type        = string
}