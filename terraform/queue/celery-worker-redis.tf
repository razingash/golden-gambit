resource "kubernetes_deployment" "worker-redis" {
  metadata {
    name = "worker-redis"
    namespace = var.celery_workers_namespace
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "worker-redis"
      }
    }
    template {
      metadata {
        labels = {
          app = "worker-redis"
        }
      }
      spec {
        container {
          name = "worker-redis"
          image = var.backend_image
          image_pull_policy = "Never"
          command= ["sh", "-c", "sleep 25 && celery -A macroeconomics_simulator worker -l info --queues=redis_queue"]
          env {
            name = "DJANGO_SETTINGS_MODULE"
            value = "macroeconomics_simulator.settings.kuberized"
          }
          env {
            name = "CELERY_BROKER_URL"
            value = "redis://redis.backend-services.svc.cluster.local:6379/1"
          }
          volume_mount {
            mount_path = "/app/media"
            name       = "django-mediafiles-storage"
          }
        }
        volume {
          name = "django-mediafiles-storage"
          persistent_volume_claim {
            claim_name = var.django_mediafiles_for_workers_pvc_name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "worker-redis-service" {
  metadata {
    name = "worker-redis"
    namespace = var.celery_workers_namespace
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