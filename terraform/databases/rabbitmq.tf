resource "kubernetes_deployment" "rabbitmq" {
  metadata {
    name = "rabbitmq"
    namespace = var.backend_services_namespace
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
          env {
            name  = "RABBITMQ_DEFAULT_USER"
            value = "admin"
          }
          env {
            name  = "RABBITMQ_DEFAULT_PASS"
            value = "admin"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "rabbitmq-service" {
  metadata {
    name = "rabbitmq"
    namespace = var.backend_services_namespace
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