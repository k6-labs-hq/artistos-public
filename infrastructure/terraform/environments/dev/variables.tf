variable "cluster_name" {
  type = string
}

variable "cluster_endpoint" {
  type = string
}

variable "cluster_ca_certificate" {
  type = string
}

variable "cluster_token" {
  type      = string
  sensitive = true
}

variable "app_image" {
  type = string
}
