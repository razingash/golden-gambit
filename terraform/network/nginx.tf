resource "kubernetes_deployment" "nginx" {
  metadata {
    name = "nginx"
    namespace = "frontend"
  }
  spec {
    replicas = "1"
    template {
      metadata {
        labels = {
          app = "nginx"
        }
      }
      spec {
        container {
          name = "nginx"
          image = "nginx"
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

resource "kubernetes_service" "nginx-service" {
  metadata {
    name = "nginx"
    namespace = "frontend"
  }
  spec {
    type = "NodePort"
    port {
      port = 80
      target_port = "80"
    }
    selector = {
      app = "nginx"
    }
  }
}