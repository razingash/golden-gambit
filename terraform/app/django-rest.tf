resource "kubernetes_deployment" "django_rest" {
  metadata {
    name = "django-rest"
    namespace = var.backend_namespace
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "django-rest"
      }
    }
    template {
      metadata {
        labels = {
          app = "django-rest"
        }
      }
      spec {
        container {
          image = var.backend_image
          name = "django-rest"
          image_pull_policy = "Never"
          port {
            container_port = 8000
          }
          env {
            name = "DJANGO_SETTINGS_MODULE"
            value = "macroeconomics_simulator.settings.kuberized"
          }
          command = [
            "/bin/sh", "-c", "python manage.py initialization && python manage.py runserver 0.0.0.0:8000 --settings=macroeconomics_simulator.settings.kuberized"
          ]
          volume_mount {
            mount_path = "/app/media"
            name       = "django-mediafiles-storage"
          }
        }
        volume {
          name = "django-mediafiles-storage"
          persistent_volume_claim {
            claim_name = var.django_mediafiles_pvc_name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "django_rest_service" {
  metadata {
    name = "django-rest"
    namespace = var.backend_namespace
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