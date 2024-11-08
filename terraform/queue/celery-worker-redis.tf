resource "kubernetes_deployment" "worker-redis" {
  metadata {
    name = "worker-redis"
    namespace = "celery-workers"
  }
  spec {
    replicas = "1"
    template {
      metadata {
        labels = {
          app = "worker-redis"
        }
      }
      spec {
        container {
          name = "worker-redis"
          image = module.docker_image_module.backend_image_latest
          command= ["sh", "-c", "sleep 25 && celery -A macroeconomics_simulator worker -l info --queues=redis_queue"]
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

resource "kubernetes_service" "worker-redis-service" {
  metadata {
    name = "worker-redis"
    namespace = "celery-workers"
  }
  spec {
    type = "ClusterIP"
    port {
      port = 8000
      target_port = "8000"
    }
    selector = {
      app = "worker-redis"
    }
  }
}