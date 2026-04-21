# Hetzner infra for ArtistOS production.
# Provision: VM + firewall + private network + object storage bucket.
# Managed Postgres is provisioned separately via console (Terraform provider
# for Hetzner managed DB is still in alpha as of 2026).

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.48"
    }
  }

  # State stored in Hetzner Object Storage (S3-compatible).
  # Create the bucket manually once, then uncomment and fill in.
  # backend "s3" {
  #   bucket                      = "xr7-terraform-state"
  #   key                         = "hetzner/prod/terraform.tfstate"
  #   region                      = "auto"
  #   endpoints                   = { s3 = "https://fsn1.your-objectstorage.com" }
  #   skip_credentials_validation = true
  #   skip_region_validation      = true
  #   skip_requesting_account_id  = true
  #   use_path_style              = true
  # }
}

provider "hcloud" {
  # HCLOUD_TOKEN env var
}

variable "environment" {
  description = "Environment name (prod, staging)"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Hetzner datacenter location"
  type        = string
  default     = "fsn1" # Falkenstein, Germany
}

variable "server_type" {
  description = "VM size"
  type        = string
  default     = "cpx21" # 3 vCPU, 4GB RAM, 80GB SSD
}

variable "ssh_key_names" {
  description = "Names of SSH keys already uploaded to Hetzner console"
  type        = list(string)
}

# Private network for app ↔ DB ↔ storage traffic
resource "hcloud_network" "xr7" {
  name     = "xr7-${var.environment}"
  ip_range = "10.0.0.0/16"
}

resource "hcloud_network_subnet" "xr7_private" {
  network_id   = hcloud_network.xr7.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.0.1.0/24"
}

# Firewall: only 22 + 80 + 443 open to the world
resource "hcloud_firewall" "xr7" {
  name = "xr7-${var.environment}"

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = [
      "0.0.0.0/0",
      "::/0",
    ]
  }

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "80"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}

# App VM
resource "hcloud_server" "xr7_app" {
  name        = "xr7-${var.environment}-app"
  image       = "ubuntu-24.04"
  server_type = var.server_type
  location    = var.location
  ssh_keys    = var.ssh_key_names

  firewall_ids = [hcloud_firewall.xr7.id]

  network {
    network_id = hcloud_network.xr7.id
    ip         = "10.0.1.10"
  }

  user_data = <<-EOF
              #!/bin/bash
              set -euo pipefail
              apt-get update && apt-get upgrade -y
              apt-get install -y docker.io docker-compose-plugin git ufw fail2ban

              # Lock SSH to key-only
              sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
              systemctl restart ssh

              # Enable Docker on boot
              systemctl enable docker
              systemctl start docker

              # Prep app directory
              mkdir -p /opt/artistos
              chown root:root /opt/artistos
              EOF

  labels = {
    app         = "xr7"
    environment = var.environment
    role        = "app"
  }
}

# Load balancer in front of the VM (enables zero-downtime deploys + easy scale-out later)
resource "hcloud_load_balancer" "xr7" {
  name               = "xr7-${var.environment}"
  load_balancer_type = "lb11"
  location           = var.location
}

resource "hcloud_load_balancer_network" "xr7" {
  load_balancer_id = hcloud_load_balancer.xr7.id
  network_id       = hcloud_network.xr7.id
}

resource "hcloud_load_balancer_target" "xr7_app" {
  type             = "server"
  load_balancer_id = hcloud_load_balancer.xr7.id
  server_id        = hcloud_server.xr7_app.id
  use_private_ip   = true
  depends_on       = [hcloud_load_balancer_network.xr7]
}

resource "hcloud_load_balancer_service" "xr7_https" {
  load_balancer_id = hcloud_load_balancer.xr7.id
  protocol         = "tcp"
  listen_port      = 443
  destination_port = 443
}

resource "hcloud_load_balancer_service" "xr7_http" {
  load_balancer_id = hcloud_load_balancer.xr7.id
  protocol         = "tcp"
  listen_port      = 80
  destination_port = 80
}
