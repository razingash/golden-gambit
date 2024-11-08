terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "3.0.2"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
  }
}

resource "docker_image" "frontend_image" {
  name = "frontend-image:latest"
  build {
    path = "${path.module}/../../frontend"
    dockerfile = "${path.module}/../../frontend/Dockerfile"
  }
}

resource "docker_image" "backend_image" {
  name = "backend-image:latest"
  build {
    path = "${path.module}/../../macroeconomics_simulator"
    dockerfile = "${path.module}/../../macroeconomics_simulator/Dockerfile"
  }
}

output "backend_image_latest" {
  value = docker_image.backend_image.latest
}