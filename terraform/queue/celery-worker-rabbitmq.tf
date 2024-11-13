resource "kubernetes_deployment" "worker-rabbitmq" {
  metadata {
    name = "worker-rabbitmq"
    namespace = var.celery_workers_namespace
  }
  spec {
    replicas = "1" # Change to 3
    selector {
      match_labels = {
        app = "worker-rabbitmq"
      }
    }
    template {
      metadata {
        labels = {
          app = "worker-rabbitmq"
        }
      }
      spec {
        container {
          name = "worker-rabbitmq"
          image = module.docker_image_module.backend_image
          command= ["sh", "-c", "sleep 25 && celery -A macroeconomics_simulator worker -l info --queues=rabbitmq_queue"]
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

resource "kubernetes_service" "worker-rabbitmq-service" {
  metadata {
    name = "worker-rabbitmq"
    namespace = var.celery_workers_namespace
  }
  spec {
    type = "ClusterIP"
    port {
      port = 8000
      target_port = "8000"
    }
    selector = {
      app = "worker-rabbitmq"
    }
  }
}