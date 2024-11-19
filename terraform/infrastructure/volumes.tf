resource "kubernetes_persistent_volume" "django-mediafiles-pv" {
  metadata {
    name = "django-mediafiles-pv"
  }
  spec {
    access_modes = ["ReadWriteMany"]
    capacity     = {
      storage = "5Gi"
    }
    persistent_volume_reclaim_policy = "Retain"
    persistent_volume_source {
      host_path {
        path = "/mnt/data/media"
      }
    }
  }
  depends_on = [kubernetes_namespace.backend]
}

resource "kubernetes_persistent_volume_claim" "django-mediafiles-pvc" {
  metadata {
    generate_name = "django-mediafiles-pvc"
    namespace = kubernetes_namespace.backend.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
  }
  depends_on = [kubernetes_namespace.backend]
}

resource "kubernetes_persistent_volume_claim" "django-mediafiles-for-workers-pvc" {
  metadata {
    generate_name = "django-mediafiles-pvc"
    namespace = kubernetes_namespace.celery-workers.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
  }
  depends_on = [kubernetes_namespace.backend]
}

output "django_mediafiles_pvc_name" {
  value = kubernetes_persistent_volume_claim.django-mediafiles-pvc.metadata[0].name
}

output "django_mediafiles_for_workers_pvc" {
  value = kubernetes_persistent_volume_claim.django-mediafiles-for-workers-pvc.metadata[0].name
}