resource "kubernetes_config_map" "prometheus-config" {
  metadata {
    name = "prometheus-config"
    namespace = var.monitoring_namespace
  }
  data = {
    "prometheus.yml" = <<-EOT
      global:
      scrape_interval: 15s

      scrape_configs:
        - job_name: "prometheus"
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            - source_labels: [__address__]
              regex: ^prometheus\.monitoring\.svc\.cluster\.local:9090$
              action: keep
          static_configs:
            - targets: ["prometheus.monitoring.svc.cluster.local:9090"]

        - job_name: "rabbitmq"
          kubernetes_sd_configs:
            - role: service
          relabel_configs:
            - source_labels: [__meta_kubernetes_service_name]
              regex: ^exporter-rabbitmq$
              target_label: service
              action: keep
          metric_relabel_configs:
            - source_labels: [__name__]
              regex: ^rabbitmq_.*
              action: keep
          static_configs:
            - targets: ["exporter-rabbitmq.monitoring.svc.cluster.local:9419"]

        - job_name: "redis"
          kubernetes_sd_configs:
            - role: service
          relabel_configs:
            - source_labels: [__meta_kubernetes_service_name]
              regex: ^exporter-redis$
              action: keep
          static_configs:
            - targets: ["exporter-redis.monitoring.svc.cluster.local:9121"]

        - job_name: "postgres"
          kubernetes_sd_configs:
            - role: service
          relabel_configs:
            - source_labels: [__meta_kubernetes_service_name]
              regex: ^exporter-postgres$
              action: keep
          metric_relabel_configs:
            - source_labels: [__name__]
              regex: ^postgres_.*
              action: keep
          static_configs:
            - targets: ["exporter-postgres.monitoring.svc.cluster.local:9187"]

        - job_name: 'kubernetes-nodes'
          kubernetes_sd_configs:
            - role: node
          metrics_path: /metrics/cadvisor
          scheme: https
          tls_config:
            ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
            insecure_skip_verify: true
          bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
          relabel_configs:
            - source_labels: [__meta_kubernetes_node_name]
              target_label: node
              action: replace
    EOT
  }
}


resource "kubernetes_deployment" "prometheus" {
  metadata {
    name = "prometheus"
    namespace = var.monitoring_namespace
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
            mount_path = "/etc/prometheus"
            name       = "prometheus=config"
          }
          args = ["--config.file=/etc/prometheus/prometheus.yml"]
        }
        volume {
          name = kubernetes_config_map.prometheus-config.metadata[0].name
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
    namespace = var.monitoring_namespace
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
