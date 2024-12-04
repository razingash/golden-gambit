resource "kubernetes_stateful_set" "redis" {
  metadata {
    name = "redis"
    namespace = var.backend_services_namespace
  }
  spec {
    service_name = "redis"
    replicas = "1"
    selector {
      match_labels = {
        app = "redis"
      }
    }
    template {
      metadata {
        labels = {
          app = "redis"
        }
      }
      spec {
        container {
          name = "redis"
          image = "redis:7.2.4"
          port {
            container_port = 6379
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "redis-service" {
  metadata {
    name = "redis"
    namespace = var.backend_services_namespace
  }
  spec {
    type = "ClusterIP"
    port {
      port = 6379
      target_port = "6379"
    }
    selector = {
      app = "redis"
    }
  }
}