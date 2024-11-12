resource "kubernetes_deployment" "celery-beat" {
  metadata {
    name = "celery-beat"
    namespace = var.celery_beat_namespace
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "celery-beat"
      }
    }
    template {
      metadata {
        labels = {
          app = "celery-beat"
        }
      }
      spec {
        container {
          name = "celery-beat"
          image = module.docker_image_module.backend_image_latest
          command = ["sh", "-c", "sleep 30 && celery -A macroeconomics_simulator beat -l INFO"]
          env {
            name = "DJANGO_SETTINGS_MODULE"
            value = "macroeconomics_simulator.settings.kuberized"
          }
        }
        restart_policy = "Always"
      }
    }
  }
}