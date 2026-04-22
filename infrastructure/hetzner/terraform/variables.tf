variable "environment" {
  description = "Environment name: qa or prod. Drives resource naming and domain."
  type        = string
  validation {
    condition     = contains(["qa", "prod"], var.environment)
    error_message = "environment must be either 'qa' or 'prod'."
  }
}

variable "location" {
  description = "Hetzner datacenter location"
  type        = string
  default     = "fsn1" # Falkenstein, Germany
}

variable "server_type" {
  description = "VM size"
  type        = string
  default     = "cpx21" # 3 vCPU, 4GB RAM, 80GB SSD, €5.83/mo
}

variable "ssh_key_names" {
  description = "Names of SSH keys already uploaded to Hetzner console. Prod should be admins only."
  type        = list(string)
}

variable "product_domain" {
  description = "Product subdomain (e.g. xr7.k6-labs.com). Hostnames become api.<product_domain> / app.<product_domain> for prod and api.qa.<product_domain> / app.qa.<product_domain> for QA. Leaves api.k6-labs.com free for other products (e.g. arcos7)."
  type        = string
  default     = "xr7.k6-labs.com"
}

locals {
  fqdn_api       = var.environment == "prod" ? "api.${var.product_domain}" : "api.qa.${var.product_domain}"
  fqdn_frontend  = var.environment == "prod" ? "app.${var.product_domain}" : "app.qa.${var.product_domain}"
  resource_name  = "xr7-${var.environment}"
  private_subnet = var.environment == "prod" ? "10.0.1.0/24" : "10.0.2.0/24"
}
