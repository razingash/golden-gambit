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


provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "infrastructure" {
  source = "./infrastructure"
}

module "databases" {
  source = "./databases"
  depends_on = [module.infrastructure]

  backend_namespace = module.infrastructure.backend_namespace
}

module "app" {
  source = "./app"
  depends_on = [module.databases]

  backend_namespace = module.infrastructure.backend_namespace
  frontend_namespace = module.infrastructure.frontend_namespace
  frontend_image = module.infrastructure.frontend_image
  backend_image = module.infrastructure.backend_image
}

module "queue" {
  source = "./queue"
  depends_on = [module.app]

  celery_beat_namespace = module.infrastructure.celery_beat_namespace
  celery_workers_namespace = module.infrastructure.celery_workers_namespace
  backend_image = module.infrastructure.backend_image
}

module "monitoring" {
  source = "./monitoring"
  depends_on = [module.queue]

  monitoring_namespace = module.infrastructure.monitoring_namespace
}