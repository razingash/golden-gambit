terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

variable "monitoring_namespace" {
  description = "Namespace for the monitoring services"
  type        = string
}