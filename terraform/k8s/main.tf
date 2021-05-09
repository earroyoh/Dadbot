provider "kubernetes" {
  config_path    = "~/.kube/admin.conf"
  config_context = "kubernetes-admin@kubernetes"
}

resource "kubernetes_namespace" "rasa" {
  metadata {
    name = "rasa"
  }
}

resource "kubernetes_deployment" "dadbot-web-deployment" {
  metadata {
    name = "dadbot-web-deployment"
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
              memory = "1024Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "50Mi"
            }
          }

          #liveness_probe {
          #  http_get {
          #    path = "/health"
          #    port = 8000

              #http_header {
              #  name  = "X-Custom-Header"
              #  value = "Awesome"
              #}
          #  }

          #  initial_delay_seconds = 3
          #  period_seconds        = 3
          #}
        }
      }
    }
  }  
}

resource "kubernetes_deployment" "dadbot-actions-deployment" {
  metadata {
    name = "dadbot-actions-deployment"
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

resource "kubernetes_deployment" "dadbot-api-deployment" {
  metadata {
    name = "dadbot-api-deployment"
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
          port {
            container_port = 5005
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

resource "kubernetes_service" "dadbot-web" {
  metadata {
    name = "dadbot-web"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web-deployment.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8000
      target_port = 8000
    }

    type = "LoadBalancer"
    external_ips = [ "192.168.1.101" ]
  }
}

resource "kubernetes_service" "dadbot-api" {
  metadata {
    name = "dadbot-api"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web-deployment.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 5005
      target_port = 5005
    }

    type = "LoadBalancer"
    external_ips = [ "192.168.1.101" ]
  }
}

resource "kubernetes_service" "dadbot-actions" {
  metadata {
    name = "dadbot-actions"
    namespace = kubernetes_namespace.rasa.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.dadbot-web-deployment.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 5055
      target_port = 5055
    }

    type = "LoadBalancer"
    external_ips = [ "192.168.1.101" ]
  }
}
