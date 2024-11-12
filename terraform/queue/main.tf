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

variable "celery_beat_namespace" {
  description = "Namespace for celery beat service"
  type        = string
}

variable "celery_workers_namespace" {
  description = "Namespace for celery workers services"
  type        = string
}