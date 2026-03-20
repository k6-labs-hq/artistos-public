output "namespace" {
  description = "Namespace where XR7 platform resources are deployed."
  value       = kubernetes_namespace.xr7.metadata[0].name
}

output "runtime_config_map" {
  description = "Name of runtime config map consumed by deploy jobs."
  value       = kubernetes_config_map.xr7_runtime.metadata[0].name
}
