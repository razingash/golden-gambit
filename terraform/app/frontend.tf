resource "kubernetes_deployment" "nginx" {
  metadata {
    name = "nginx"
    namespace = var.frontend_namespace
  }
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
          command = [
            "/bin/sh", "-c", "if [ ! -f /etc/nginx/ssl/nginx.key ]; then mkdir -p /etc/nginx/ssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt -subj '/CN=localhost'; fi && nginx -g 'daemon off;'"
          ]
          env {
            name = "PORT"
            value = "80"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "nginx-service" {
  metadata {
    name = "nginx"
    namespace = var.frontend_namespace
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
/* вылетает ошибка
Failed to create Ingress 'frontend/nginx-ingress' because: the server could not find the requested resource (post ingresses.extensions)
resource "kubernetes_ingress" "nginx-ingress" {
  metadata {
    name = "nginx-ingress"
    namespace = var.frontend_namespace
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/"
    }
  }
  spec {
    ingress_class_name = "ngixn"
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
*/