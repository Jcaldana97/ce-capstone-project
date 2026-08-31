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

#
#output "app_instance_ids" {
#  description = "App instance IDs"
#  value       = aws_instance.app[*].id
#}

#output "target_group_arn" {
#  description = "Target group ARN"
#  value       = aws_lb_target_group.app.arn
#}