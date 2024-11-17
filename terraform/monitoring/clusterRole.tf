resource "kubernetes_service_account" "v1" {
  metadata {
    name = "prometheus"
    namespace = var.monitoring_namespace
  }
}

resource "kubernetes_cluster_role" "prometheus" {
  metadata {
    name = "prometheus"
  }
  rule {
    api_groups = [""]
    resources = ["nodes", "nodes/proxy"]
    verbs = ["get", "list"]
  }
  rule {
    api_groups = [""]
    resources = ["pods", "services"]
    verbs = ["get", "list"]
  }
  rule {
    api_groups = [""]
    resources = ["nodes/metrics"]
    verbs = ["get"]
  }
}

resource "kubernetes_cluster_role_binding" "prometheus" {
  metadata {
    name = "prometheus"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.prometheus.metadata[0].name
  }
  subject {
    kind = "ServiceAccount"
    name = "prometheus"
    namespace = var.monitoring_namespace
  }
}
