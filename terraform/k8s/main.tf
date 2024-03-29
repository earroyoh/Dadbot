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
  config_context = var.k8s-context
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

data "kubernetes_namespace" "rasa" {
  metadata {
    name = var.dadbot-namespace
  }
}

resource "kubernetes_namespace" "rasa" {
  metadata {
    name = var.dadbot-namespace
  }
}

resource "kubernetes_deployment" "dadbot-web" {
  metadata {
    name = "dadbot-web"
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
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
          image = "${var.registry}dadbot-web:1.0"
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
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
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
          image = "${var.registry}dadbot-actions:1.0"
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
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
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
          image = "${var.registry}dadbot-api:1.0"
          name  = "dadbot-connector"
          env {
            name = "RASA_TELEMETRY_ENABLED"
            value = "false"
          }
          env {
            name = "PYTHONPATH"
            value = "/app/.local/:/usr/local/"
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

resource "kubernetes_deployment" "dadbot-speaker" {
  metadata {
    name = "dadbot-speaker"
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
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
          image = "${var.registry}dadbot-speaker:1.0"
          name  = "dadbot-actions"
          port {
            container_port = 5006
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
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
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

    type = "NodePort"
    #external_ips = [ "${var.external-ip}" ]
  }
}

resource "kubernetes_service" "dadbot-api" {
  metadata {
    name = "dadbot-api"
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
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

    type = "NodePort"
    #external_ips = [ "${var.external-ip}" ]
  }
}

resource "kubernetes_service" "dadbot-speaker" {
  metadata {
    name = "dadbot-speaker"
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 5006
      target_port = 5006
    }

    type = "NodePort"
    #external_ips = [ "${var.external-ip}" ]
  }
}

resource "kubernetes_secret" "this" {
  metadata {
    name = "dadbot-tls-secret"
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
  }

  data = {
    "tls.crt" = file("${var.workspace-dir}/dadbot.crt")
    "tls.key" = file("${var.workspace-dir}/dadbot.key")
  }

  type = "kubernetes.io/tls"
} 

resource "helm_release" "dadbot-ingress-nginx" {
  name       = "dadbot"
  namespace  = data.kubernetes_namespace.rasa.metadata.0.name

  repository = "https://charts.bitnami.com/bitnami"
  #repository = "https://helm.nginx.com/stable"
  chart      = "nginx-ingress-controller"

  set {
    name  = "service.type"
    value = "LoadBalancer"
  }
}

resource "kubernetes_ingress" "dadbot_ingress" {
  wait_for_load_balancer = false
  metadata {
    name = "dadbot-ingress"
    namespace = data.kubernetes_namespace.rasa.metadata.0.name
    labels = {
      app = "dadbotapp"
    }
    annotations = {
      "nginx.ingress.kubernetes.io/ingress.enabled" : "true"
      "nginx.ingress.kubernetes.io/rewrite-target": "/"
      "nginx.ingress.kubernetes.io/backend-protocol": "HTTPS"
      "nginx.ingress.kubernetes.io/upstream-vhost": var.dadbot-web-url
      "nginx.ingress.kubernetes.io/configuration-snippet": "proxy_ssl_name ${kubernetes_deployment.dadbot-web.metadata.0.name}.${data.kubernetes_namespace.rasa.metadata.0.name}.svc.cluster.local;"
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
            service_name = kubernetes_service.dadbot-web.metadata.0.name
            service_port = 8000
          }

          path = "/audios/*"
        }

        path {
          backend {
            service_name = kubernetes_service.dadbot-web.metadata.0.name
            service_port = 8000
          }

          path = "/static/*"
        }

        path {
          backend {
            service_name = kubernetes_service.dadbot-api.metadata.0.name
            service_port =  5005
          }

          path = "/webhooks/voice/webhook/*"
        }

        path {
          backend {
            service_name = kubernetes_service.dadbot-speaker.metadata.0.name
            service_port =  5006
          }

          path = "/get/*"
        }
        
        path {
          backend {
            service_name = kubernetes_service.dadbot-speaker.metadata.0.name
            service_port =  5006
          }

          path = "/put/*"
        }      
      }
    }

    tls {
      secret_name = "dadbot-tls-secret"
    }
  }
}
