resource "kubernetes_deployment" "redis" {
  metadata {
    name = "redis"
    namespace = "backend-services"
  }
  spec {
    replicas = "1"
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
    namespace = "backend-services"
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