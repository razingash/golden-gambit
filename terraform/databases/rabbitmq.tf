resource "kubernetes_deployment" "rabbitmq" {
  metadata {
    name = "rabbitmq"
    namespace = var.backend_namespace
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "rabbitmq"
      }
    }
    template {
      metadata {
        labels = {
          app = "rabbitmq"
        }
      }
      spec {
        container {
          name = "rabbitmq"
          image = "rabbitmq:4.0.3"
          port {
            container_port = 5672
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "rabbitmq-service" {
  metadata {
    name = "rabbitmq"
    namespace = var.backend_namespace
  }
  spec {
    type = "ClusterIP"
    port {
      port = 5672
      target_port = "5672"
    }
    selector = {
      app = "rabbitmq"
    }
  }
}