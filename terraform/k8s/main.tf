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

resource "kubernetes_namespace" "rasa" {
  metadata {
    name = "rasa"
  }
}

resource "kubernetes_deployment" "dadbot-web" {
  metadata {
    name = "dadbot-web"
    namespace = kubernetes_namespace.rasa.metadata.0.name
    labels = {
      app = "dadbotapp"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "dadbotapp"
      }
    }

    template {
      metadata {
        labels = {
          app = "dadbotapp"
        }
      }

      spec {
        container {
          image = "dadbot-web:1.0"
          name  = "dadbot-web"
          port {
            container_port = 8000
          }
          resources {
            limits = {
              cpu    = "0.5"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "50Mi"
            }
          }

          #liveness_probe {
          #  http_get {
          #    path = "/health"
          #    port = 80

          #    http_header {
          #      name  = "X-Custom-Header"
          #      value = "Health"
          #    }
          #  }

          #  initial_delay_seconds = 3
          #  period_seconds        = 3
          #}
        }
      }
    }
  }  
}

resource "kubernetes_deployment" "dadbot-actions" {
  metadata {
    name = "dadbot-actions"
    namespace = kubernetes_namespace.rasa.metadata.0.name
    labels = {
      app = "dadbotapp"
    }
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "dadbotapp"
      }
    }
    template {
      metadata {
        labels = {
          app = "dadbotapp"
        }
      }
      spec {
        container {
          image = "dadbot-actions:1.0"
          name  = "dadbot-actions"
          env { 
             name = "OPENAI_API_KEY"
             value = var.OPENAI_API_KEY
          }
          port {
            container_port = 5055
          }
          resources {
            limits = {
              cpu    = "0.5"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "50Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "dadbot-connector" {
  metadata {
    name = "dadbot-connector"
    namespace = kubernetes_namespace.rasa.metadata.0.name
    labels = {
      app = "dadbotapp"
    }
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "dadbotapp"
      }
    }
    template {
      metadata {
        labels = {
          app = "dadbotapp"
        }
      }
      spec {
        container {
          image = "dadbot-api:1.0"
          name  = "dadbot-connector"
          env {
            name = "RASA_TELEMETRY_ENABLED"
            value = "false"
          }
          port {
            container_port = 5005
          }
          resources {
            limits = {
              cpu    = "0.5"
              memory = "2048Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "50Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "dadbot-web" {
  metadata {
    name = "dadbot-web"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8000
      target_port = 8000
    }

    type = "LoadBalancer"
    external_ips = [ "${var.external-ip}" ]
  }
}

resource "kubernetes_service" "dadbot-api" {
  metadata {
    name = "dadbot-api"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 5005
      target_port = 5005
    }

    type = "LoadBalancer"
    external_ips = [ "${var.external-ip}" ]
  }
}

resource "kubernetes_service" "dadbot-actions" {
  metadata {
    name = "dadbot-actions"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 5055
      target_port = 5055
    }

    type = "LoadBalancer"
    external_ips = [ "${var.external-ip}" ]
  }
}

resource "kubernetes_secret" "this" {
  metadata {
    name = "dadbot-tls-secret"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }

  data = {
    "tls.crt" = file("${var.workspace-dir}/dadbot.crt")
    "tls.key" = file("${var.workspace-dir}/dadbot.key")
  }

  type = "kubernetes.io/tls"
} 

resource "kubernetes_ingress" "dadbot_ingress" {
  #wait_for_load_balancer = true
  metadata {
    name = "dadbot-ingress"
    namespace = kubernetes_namespace.rasa.metadata.0.name
    labels = {
      app = "dadbotapp"
    }
    annotations = {
      "kubernetes.io/ingress.class" : "nginx"
    }
  }

  spec {
    backend {
      service_name = kubernetes_service.dadbot-web.metadata.0.name
      service_port = 8000
    }

    rule {
      host = var.dadbot-web-url
      http {
        path {
          backend {
            service_name = kubernetes_service.dadbot-web.metadata.0.name
            service_port = 8000
          }

          path = "/health"
        }

        path {
          backend {
            service_name = kubernetes_service.dadbot-web.metadata.0.name
            service_port = 8000
          }

          path = "/"
        }

        path {
          backend {
            service_name = kubernetes_service.dadbot-api.metadata.0.name
            service_port =  5005
          }

          path = "/webhooks/voice/webhook/*"
        }
      }
    }

    tls {
      secret_name = "dadbot-tls-secret"
    }
  }
}
