resource "kubernetes_deployment" "react" {
  metadata {
    name = "react"
    namespace = "frontend"
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "react"
      }
    }
    template {
      metadata {
        labels = {
          app = "react"
        }
      }
      spec {
        container {
          name = "react"
          image = module.docker_image_module.frontend_image_latest
          port {
            container_port = 3001
          }
          command = ["sh", "-c", "npm start"]
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