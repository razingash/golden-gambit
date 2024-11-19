resource "kubernetes_deployment" "postgres" {
  metadata {
    name = "postgres"
    namespace = var.backend_services_namespace
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "postgres"
      }
    }
    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }
      spec {
        container {
          name = "postgres"
          image = "postgres:16"
          port {
            container_port = 5432
          }
          env {
            name = "POSTGRES_DB"
            value = "macroeconomics_simulator"
          }
          env {
            name = "POSTGRES_USER"
            value = "postgres"
          }
          env {
            name = "POSTGRES_PASSWORD"
            value = "root"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "postgres_service" {
  metadata {
    name = "postgres"
    namespace = var.backend_services_namespace
  }
  spec {
    type = "ClusterIP"
    selector = {
      app = "postgres"
    }
    port {
      port = 5432
      target_port = "5432"
    }
  }
}