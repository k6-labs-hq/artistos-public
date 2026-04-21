output "app_server_ipv4" {
  description = "Public IPv4 of the app VM (for SSH)"
  value       = hcloud_server.xr7_app.ipv4_address
}

output "app_server_private_ip" {
  description = "Private IP within the xr7 network"
  value       = hcloud_server.xr7_app.network.*.ip
}

output "load_balancer_ipv4" {
  description = "Public IPv4 of the load balancer (point DNS here)"
  value       = hcloud_load_balancer.xr7.ipv4
}

output "network_id" {
  description = "Private network ID for attaching additional services"
  value       = hcloud_network.xr7.id
}
