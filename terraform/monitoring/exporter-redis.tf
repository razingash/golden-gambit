resource "kubernetes_deployment" "exporter_redis" {
  metadata {
    name = "exporter-redis"
    namespace = var.monitoring_namespace
    labels = {
      app = "exporter-redis"
    }
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "exporter-redis"
      }
    }
    template {
      metadata {
        labels = {
          app = "exporter-redis"
        }
      }
      spec {
        container {
          name = "exporter-redis"
          image = "oliver006/redis_exporter"
          port {
            container_port = 9121
          }
          env {
            name = "REDIS_ADDR"
            value = "redis.backend-services.svc.cluster.local:6379"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "exporter_redis" {
  metadata {
    name = "exporter-redis"
    namespace = var.monitoring_namespace
    labels = {
      app = "exporter-redis"
    }
  }
  spec {
    port {
      port = 9121
      target_port = "9121"
    }
    selector = {
      app = "exporter-redis"
    }
  }
}