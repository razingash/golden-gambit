resource "kubernetes_deployment" "grafana" {
  metadata {
    name = "grafana"
    namespace = "monitoring"
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "grafana"
      }
    }
    template {
      metadata {
        labels = {
          app = "grafana"
        }
      }
      spec {
        container {
          name = "grafana"
          image = "grafana/grafana:latest"
          port {
            container_port = 3000
          }
          env {
            name = "GF_SECURITY_ADMIN_USER"
            value = "admin"
          }
          env {
            name = "GF_SECURITY_ADMIN_PASSWORD"
            value = "admin"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "grafana-service" {
  metadata {
    name = "grafana"
    namespace = "monitoring"
  }
  spec {
    type = "NodePort"
    port {
      port = 3000
      target_port = "3000"
    }
    selector = {
      app = "grafana"
    }
  }
}