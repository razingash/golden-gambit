terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

module "docker_image_module" {
  source = "../infrastructure/"
}

variable "backend_namespace" {
  description = "Namespace for the backend services"
  type        = string
}

variable "frontend_namespace" {
  description = "Namespace for the frontend services"
  type        = string
}