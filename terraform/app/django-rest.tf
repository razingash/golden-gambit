resource "kubernetes_deployment" "django_rest" {
  metadata {
    name = "django-rest"
    namespace = "backend"
    labels = {
      app = "django-rest"
    }
  }
  spec {
    replicas = "1"
    template {
      metadata {
        labels = {
          app = "django-rest"
        }
      }
      spec {
        container {
          image = docker_image.backend_image.latest
          name = "django-rest"
          port {
            container_port = 8000
          }
          env {
            name = "DJANGO_SETTINGS_MODULE"
            value = "macroeconomics_simulator.settings.kuberized"
          }
          volume_mount {
            mount_path = "/app/media"
            name       = "django-mediafiles-storage"
          }
        }
        volume {
          name = "django-mediafiles-storage"
          persistent_volume_claim {
            claim_name = "django-mediafiles-pvc"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "django_rest_service" {
  metadata {
    name = "django-rest"
    namespace = "backend"
  }
  spec {
    type = "ClusterIP"
    selector = {
      app = "django-rest"
    }
    port {
      port = 8000
      target_port = "8000"
    }
  }
}
