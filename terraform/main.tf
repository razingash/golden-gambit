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
  config_path = "~/.kube/config" #??????
}

module "infrastructure" {
  source = "./infrastructure"
}

module "databases" {
  source = "./databases"
  depends_on = [module.infrastructure]
}

module "app" {
  source = "./app"
  depends_on = [module.databases]
}

module "network" {
  source = "./network"
  depends_on = [module.app]
}

module "queue" {
  source = "./queue"
  depends_on = [module.network]
}