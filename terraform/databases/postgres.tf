resource "kubernetes_stateful_set" "postgres" {
  metadata {
    name = "postgres"
    namespace = var.backend_services_namespace
  }
  spec {
    service_name = "postgres"
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
          volume_mount {
            mount_path = "/var/lib/postgresql/data"
            name       = "postgres-data"
          }
        }
      }
    }
    volume_claim_template {
      metadata {
        name = "postgres-data"
      }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = {
            storage = "10Gi"
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