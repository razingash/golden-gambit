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

resource "docker_image" "backend_image" {
  name = "backend-image:latest"
  build {
    context = "${path.root}/../macroeconomics_simulator"
    dockerfile = "Dockerfile"
    tag = ["backend-image:latest"]
  }
}

resource "docker_image" "frontend_image" {
  name = "frontend-image:latest"
  build {
    context = "${path.root}/../frontend"
    dockerfile = "Dockerfile.terraform"
    tag = ["frontend-image:latest"]
  }
}

resource "null_resource" "load_frontend_image" {
  provisioner "local-exec" {
    command = "docker context use default && minikube image load frontend-image:latest"
  }

  triggers = {
    image_id = docker_image.frontend_image.id
  }
  depends_on = [docker_image.frontend_image]
}

resource "null_resource" "load_backend_image" {
  provisioner "local-exec" {
    command = "docker context use default && minikube image load backend-image:latest"
  }

  triggers = {
    image_id = docker_image.backend_image.id
  }
  depends_on = [docker_image.backend_image]
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "infrastructure" {
  source = "./infrastructure"
  depends_on = [null_resource.load_frontend_image, null_resource.load_backend_image]
}

module "databases" {
  source = "./databases"
  depends_on = [module.infrastructure]

  backend_services_namespace = module.infrastructure.backend_services_namespace
}

module "app" {
  source = "./app"
  depends_on = [module.databases]

  backend_namespace = module.infrastructure.backend_namespace
  frontend_namespace = module.infrastructure.frontend_namespace
  frontend_image = docker_image.frontend_image.name
  backend_image = docker_image.backend_image.name
  django_mediafiles_pvc_name = module.infrastructure.django_mediafiles_pvc_name
}
/*
module "queue" {
  source = "./queue"
  depends_on = [module.app]

  celery_beat_namespace = module.infrastructure.celery_beat_namespace
  celery_workers_namespace = module.infrastructure.celery_workers_namespace
  backend_image = docker_image.backend_image.name
  django_mediafiles_for_workers_pvc_name = module.infrastructure.django_mediafiles_for_workers_pvc
}

module "monitoring" {
  source = "./monitoring"
  depends_on = [module.queue]

  monitoring_namespace = module.infrastructure.monitoring_namespace
}*/