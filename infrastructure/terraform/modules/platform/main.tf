terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.32"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.15"
    }
  }
}

provider "kubernetes" {
  host                   = var.cluster_endpoint
  cluster_ca_certificate = var.cluster_ca_certificate
  token                  = var.cluster_token
}

provider "helm" {
  kubernetes {
    host                   = var.cluster_endpoint
    cluster_ca_certificate = var.cluster_ca_certificate
    token                  = var.cluster_token
  }
}

resource "kubernetes_namespace" "xr7" {
  metadata {
    name = var.namespace
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
      "app.kubernetes.io/part-of"          = "xr7"
      "environment"                        = var.environment
    }
  }
}

resource "helm_release" "prometheus_stack" {
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = kubernetes_namespace.xr7.metadata[0].name

  values = [
    yamlencode({
      grafana = {
        adminPassword = "replace-in-secrets-manager"
      }
      prometheus = {
        prometheusSpec = {
          retention = "15d"
        }
      }
    })
  ]
}

resource "helm_release" "otel_collector" {
  name       = "opentelemetry-collector"
  repository = "https://open-telemetry.github.io/opentelemetry-helm-charts"
  chart      = "opentelemetry-collector"
  namespace  = kubernetes_namespace.xr7.metadata[0].name

  values = [
    yamlencode({
      mode = "deployment"
      config = {
        receivers = {
          otlp = {
            protocols = {
              grpc = {}
              http = {}
            }
          }
        }
      }
    })
  ]
}

resource "kubernetes_config_map" "xr7_runtime" {
  metadata {
    name      = "xr7-runtime"
    namespace = kubernetes_namespace.xr7.metadata[0].name
  }

  data = {
    APP_IMAGE       = var.app_image
    API_REPLICAS    = tostring(var.replicas_api)
    WORKER_REPLICAS = tostring(var.replicas_worker)
  }
}
