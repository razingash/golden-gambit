resource "kubernetes_deployment" "react" {
  metadata {
    name = "react"
    namespace = "fronted"
  }
  spec {
    replicas = "1"
    template {
      metadata {
        labels = {
          app = "react"
        }
      }
      spec {
        container {
          name = "react"
          image = docker_image.frontend_image.latest
          port {
            container_port = 3001
          }
          env {
            name = "PORT"
            value = "3001"
          }
        }
      }
    }
  }
}
# add in prod REACT_APP_BASE_URL, REACT_APP_BASE_SSE_URL, REACT_APP_WEBSOCKET_URL

resource "kubernetes_service" "react-service" {
  metadata {
    name = "react"
    namespace = "frontend"
  }
  spec {
    type = "ClusterIP"
    port {
      port = 3001
      target_port = "3001"
    }
    selector = {
      app = "react"
    }
  }
}