terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 1.19"
    }
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "docker-desktop"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "kubernetes_namespace" "rasa" {
  metadata {
    name = var.dadbot-namespace
  }
}

resource "helm_release" "rasa-x" {
  name       = "dadbot"
  namespace  = kubernetes_namespace.rasa.metadata.0.name

  repository = "https://rasahq.github.io/rasa-x-helm"
  chart      = "rasa-x"

  set {
    name  = "service.type"
    value = "ClusterIP"
  }
}
