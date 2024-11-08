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

provider "docker" {}

provider "kubernetes" {
  config_path = "~/.kube/config" #??????
}

module "infrastructure" {
  source = "./infrastructure"
}

module "databases" {
  source = "./databases"
}

module "app" {
  source = "./app"
}

module "queue" {
  source = "./queue"
}

module "network" {
  source = "./network"
}
