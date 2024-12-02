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
        init_container {
          name = "generate-certificates"
          image = var.frontend_image
          image_pull_policy = "Never"
          command = [
            "/bin/sh", "-c", "if [ ! -f /etc/nginx/ssl/nginx.key ]; then mkdir -p /etc/nginx/ssl && openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt -subj '/CN=localhost'; fi"
          ]
          volume_mount {
            name       = "tls-certificates"
            mount_path = "/etc/nginx/ssl"
          }
          security_context {
            run_as_user = 0
          }
        }
        container {
          name = "nginx"
          image = var.frontend_image
          image_pull_policy = "Never"
          port {
            container_port = 443
          }
          command = [
            "nginx", "-g", "daemon off;"
          ]
          volume_mount {
            name       = "tls-certificates"
            mount_path = "/etc/nginx/ssl"
          }
        }
        volume {
          name = "tls-certificates"
          empty_dir {}
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
      name = "https"
      port = 443
      target_port = "443"
    }
    selector = {
      app = "nginx"
    }
  }
}

resource "kubernetes_ingress_v1" "nginx-ingress" {
  metadata {
    name = "nginx"
    namespace = var.frontend_namespace
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/"
      "nginx.ingress.kubernetes.io/ssl-redirect" = "true"
      "kubernetes.io/ingress.class" = "nginx"
    }
  }
  spec {
    ingress_class_name = "nginx"
    rule {
      host = "localhost"
      http {
        path {
          path = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.nginx-service.metadata[0].name
              port {
                number = 443
              }
            }
          }
        }
      }
    }
    tls {
      hosts = ["localhost"]
      secret_name = "nginx-tls"
    }
  }
}