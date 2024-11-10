resource "kubernetes_config_map" "prometheus-config" {
  metadata {
    name = "prometheus-config"
    namespace = "monitoring"
  }
  data = {
    "prometheus.yml" = <<-EOT
      global:
        scrape_interval: 15s

      scrape_configs:
        - job_name: "prometheus"
          static_configs:
            - targets: ["prometheus:9090"]

        - job_name: "rabbitmq"
          static_configs:
            - targets: ["rabbitmq-exporter:9419"]
    EOT
  }
}


resource "kubernetes_deployment" "prometheus" {
  metadata {
    name = "prometheus"
    namespace = "monitoring"
  }
  spec {
    replicas = "1"
    selector {
      match_labels = {
        app = "prometheus"
      }
    }
    template {
      metadata {
        labels = {
          app = "prometheus"
        }
      }
      spec {
        container {
          name = "prometheus"
          image = "prom/prometheus"
          port {
            container_port = 9090
          }
          volume_mount {
            mount_path = kubernetes_config_map.prometheus-config
            name       = "prometheus=config"
          }
          args = ["--config.file=/etc/prometheus/prometheus.yml"]
        }
        volume {
          name = "prometheus-config"
          config_map {
            name = "prometheus"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "prometheus-service" {
  metadata {
    name = "prometheus"
    namespace = "prometheus"
  }
  spec {
    type = "ClusterIP"
    port {
      port = 9090
      target_port = "9090"
    }
    selector = {
      app = "prometheus"
    }
  }
}
