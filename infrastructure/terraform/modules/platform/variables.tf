variable "environment" {
  description = "Environment name (dev, staging, prod)."
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace for XR7 platform workloads."
  type        = string
  default     = "xr7"
}

variable "cluster_name" {
  description = "Target Kubernetes cluster name."
  type        = string
}

variable "cluster_endpoint" {
  description = "Target Kubernetes cluster API endpoint."
  type        = string
}

variable "cluster_ca_certificate" {
  description = "Base64-decoded cluster CA certificate."
  type        = string
}

variable "cluster_token" {
  description = "Bearer token for cluster auth."
  type        = string
  sensitive   = true
}

variable "app_image" {
  description = "Container image for XR7 API and workers."
  type        = string
}

variable "replicas_api" {
  description = "Desired baseline API replicas."
  type        = number
  default     = 3
}

variable "replicas_worker" {
  description = "Desired baseline worker replicas."
  type        = number
  default     = 3
}
