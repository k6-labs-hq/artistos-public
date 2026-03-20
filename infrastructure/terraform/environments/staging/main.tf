terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }

  backend "s3" {
    bucket = "xr7-terraform-state-staging"
    key    = "platform/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

module "aws_foundation" {
  source = "../../modules/aws_foundation"

  environment     = "staging"
  region          = var.region
  cluster_name    = var.cluster_name
  vpc_cidr        = var.vpc_cidr
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
  db_name         = var.db_name
  db_username     = var.db_username
  db_password     = var.db_password
  tags            = var.tags
}

data "aws_eks_cluster_auth" "this" {
  name = module.aws_foundation.cluster_name
}

module "platform" {
  source = "../../modules/platform"

  environment            = "staging"
  namespace              = "xr7-staging"
  cluster_name           = module.aws_foundation.cluster_name
  cluster_endpoint       = module.aws_foundation.cluster_endpoint
  cluster_ca_certificate = module.aws_foundation.cluster_ca_certificate
  cluster_token          = data.aws_eks_cluster_auth.this.token
  app_image              = var.app_image
  replicas_api           = 3
  replicas_worker        = 3
}
