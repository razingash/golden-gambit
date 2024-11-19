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

variable "backend_image" {
  description = "Docker image for the backend"
  type        = string
}

variable "frontend_namespace" {
  description = "Namespace for the frontend services"
  type        = string
}

variable "frontend_image" {
  description = "Docker image for the frontend"
  type        = string
}

variable "django_mediafiles_pvc_name" {
  description = "django mediafiles"
  type        = string
}