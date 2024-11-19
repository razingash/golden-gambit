terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

variable "celery_beat_namespace" {
  description = "Namespace for celery beat service"
  type        = string
}

variable "celery_workers_namespace" {
  description = "Namespace for celery workers services"
  type        = string
}

variable "backend_image" {
  description = "Docker image for the backend"
  type        = string
}

variable "django_mediafiles_for_workers_pvc_name" {
  description = "django mediafiles"
  type        = string
}