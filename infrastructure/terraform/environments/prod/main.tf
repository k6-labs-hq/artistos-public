terraform {
  required_version = ">= 1.6.0"

  backend "s3" {
    bucket = "xr7-terraform-state-prod"
    key    = "platform/terraform.tfstate"
    region = "us-east-1"
  }
}

module "platform" {
  source = "../../modules/platform"

  environment            = "prod"
  namespace              = "xr7-prod"
  cluster_name           = var.cluster_name
  cluster_endpoint       = var.cluster_endpoint
  cluster_ca_certificate = var.cluster_ca_certificate
  cluster_token          = var.cluster_token
  app_image              = var.app_image
  replicas_api           = 6
  replicas_worker        = 6
}
