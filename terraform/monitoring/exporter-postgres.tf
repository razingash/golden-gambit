resource "kubernetes_deployment" "exporter_postgres" {
  metadata {
    name = "exporter-postgres"
    namespace = var.monitoring_namespace
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "exporter-postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "exporter-postgres"
        }
      }
      spec {
        container {
          name = "exporter-postgres"
          image = "wrouesnel/postgres_exporter"
          port {
            container_port = 9187
          }
          env {
            name = "DATA_SOURCE_NAME"
            value = "postgres.backend-services.svc.cluster.local:5432"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "exporter_postgres" {
  metadata {
    name = "exporter-postgres"
    namespace = var.monitoring_namespace
  }
  spec {
    type = "ClusterIP"
    port {
      port = 9187
      target_port = "9187"
    }
    selector = {
      app = "exporter-postgres"
    }
  }
}