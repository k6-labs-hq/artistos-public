variable "cluster_name" {
  type = string
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type = string
  default = "10.70.0.0/16"
}

variable "private_subnets" {
  type = list(string)
  default = [
    "10.70.1.0/24",
    "10.70.2.0/24",
    "10.70.3.0/24",
  ]
}

variable "public_subnets" {
  type = list(string)
  default = [
    "10.70.101.0/24",
    "10.70.102.0/24",
    "10.70.103.0/24",
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
