output "vpc_id" {
  description = "VPC identifier"
  value       = module.vpc_dev.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.vpc_dev.vpc_cidr
}

output "alb_dns_name" {
  description = "ALB DNS name — access your application here"
  value       = module.alb.alb_dns_name
}

output "alb_url" {
  description = "Full URL for the application"
  value       = module.alb.alb_url
}
