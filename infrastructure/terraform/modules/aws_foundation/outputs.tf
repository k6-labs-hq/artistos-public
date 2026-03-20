output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_ca_certificate" {
  value = base64decode(module.eks.cluster_certificate_authority_data)
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "db_endpoint" {
  value = aws_db_instance.xr7.address
}

output "db_port" {
  value = aws_db_instance.xr7.port
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.xr7.primary_endpoint_address
}

output "artifacts_bucket" {
  value = aws_s3_bucket.artifacts.bucket
}

output "kms_key_arn" {
  value = aws_kms_key.xr7.arn
}
