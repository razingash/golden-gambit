resource "kubernetes_namespace" "backend-services" {
  metadata {
    name = "backend-services"
  }
}
# the most important: PostgreSql, Redis, RabbitMq

resource "kubernetes_namespace" "backend" {
  metadata {
    name = "backend"
  }
}
# Only Django

resource "kubernetes_namespace" "frontend" {
  metadata {
    name = "frontend"
  }
}
# Nginx and React

resource "kubernetes_namespace" "celery-workers" {
  metadata {
    name = "celery-workers"
  }
}
# Redis and RabbitMq workers

resource "kubernetes_namespace" "celery-beat" {
  metadata {
    name = "celery-beat"
  }
}
# celery beat

resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}
# # Prometheus, Grafana, and all related services for getting information