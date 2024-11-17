resource "kubernetes_deployment" "exporter_rabbitmq" {
  metadata {
    name = "exporter-rabbitmq"
    namespace = var.monitoring_namespace
    labels = {
      app = "exporter-rabbitmq"
    }
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "exporter-rabbitmq"
      }
    }
    template {
      metadata {
        labels = {
          app = "exporter-rabbitmq"
        }
      }
      spec {
        container {
          name = "exporter-rabbitmq"
          image = "kbudde/rabbitmq-exporter"
          port {
            container_port = 9419
          }
          env {
            name = "RABBITMQ_URL"
            value = "rabbitmq-service.backend-services.svc.cluster.local:5672"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "exporter_rabbitmq" {
  metadata {
    name = "exporter-rabbitmq"
    namespace = var.monitoring_namespace
    labels = {
      app = "exporter-rabbitmq"
    }
  }
  spec {
    port {
      port = 9419
      target_port = "9419"
    }
    selector = {
      app = "exporter-rabbitmq"
    }
  }
}