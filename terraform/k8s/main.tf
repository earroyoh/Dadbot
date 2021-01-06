provider "kubernetes" {
  config_context = "my-context"
}

resource "kubernetes_namespace" "rasa" {
  metadata {
    name = "rasa"
  }
}
