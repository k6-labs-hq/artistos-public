variable "cluster_name" {
  type = string
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type = string
  default = "10.80.0.0/16"
}

variable "private_subnets" {
  type = list(string)
  default = [
    "10.80.1.0/24",
    "10.80.2.0/24",
    "10.80.3.0/24",
  ]
}

variable "public_subnets" {
  type = list(string)
  default = [
    "10.80.101.0/24",
    "10.80.102.0/24",
    "10.80.103.0/24",
  ]
}

variable "db_name" {
  type    = string
  default = "xr7"
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "app_image" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
