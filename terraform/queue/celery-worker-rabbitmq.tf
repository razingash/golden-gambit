resource "kubernetes_deployment" "worker-rabbitmq" {
  metadata {
    name = "worker-rabbitmq"
    namespace = var.celery_workers_namespace
  }
  spec {
    replicas = "1"
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
          image = var.backend_image
          image_pull_policy = "Never"
          command= [
            "sh", "-c", "sleep 25 && celery -A macroeconomics_simulator worker -l info --queues=rabbitmq_queue --concurrency=3"
          ]
          env {
            name = "DJANGO_SETTINGS_MODULE"
            value = "macroeconomics_simulator.settings.kuberized"
          }
          env {
            name = "CELERY_BROKER_URL"
            value = "amqp://admin:admin@rabbitmq.backend-services.svc.cluster.local:5672//"
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