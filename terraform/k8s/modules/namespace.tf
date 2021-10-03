data "kubernetes_namespace" "ns" {
  metadata {
    name = var.dadbot-namespace
  }
}

output "ns-present" {
  value = lookup(data.kubernetes_namespace.ns, "id") != null
}

output "ns-select" {
  value = data.kubernetes_namespace.ns.metadata.0.name
}