resource "kubernetes_deployment" "nginx" {
  metadata {
    name = "nginx"
    namespace = var.frontend_namespace
  }
  depends_on = [var.frontend_image]
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "nginx"
      }
    }
    template {
      metadata {
        labels = {
          app = "nginx"
        }
      }
      spec {
        container {
          name = "nginx"
          image = var.frontend_image
          image_pull_policy = "Never"
          port {
            container_port = 80
          }
          volume_mount {
            mount_path = "/etc/nginx/nginx.conf"
            name       = "nginx-config"
          }
          command = [
            "/bin/sh", "-c", "if [ ! -f /etc/nginx/ssl/nginx.key ]; then mkdir -p /etc/nginx/ssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt -subj '/CN=localhost'; fi && nginx -g 'daemon off;'"
          ]
          env {
            name = "PORT"
            value = "80"
          }
        }
        volume {
          name = "nginx-config"
          config_map {
            name = "nginx-config"
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress" "nginx-service" {
  metadata {
    name = "nginx-ingress"
    namespace = var.frontend_namespace
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/"
    }
  }
  spec {
    rule {
      host = "localhost"
      http {
        path {
          path = "/"
          backend {
            service_name = "nginx"
            service_port = "80"
          }
        }
      }
    }
  }
}