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
    generate_name = "django-mediafiles-pvc-"
    namespace = "backend"
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