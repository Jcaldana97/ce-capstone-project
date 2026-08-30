output "vpc_id" {
  description = "VPC identifier"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "alb_dns_name" {
  description = "ALB DNS name — access your application here"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "Full URL for the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "app_instance_ids" {
  description = "App instance IDs"
  value       = aws_instance.app[*].id
}

output "target_group_arn" {
  description = "Target group ARN"
  value       = aws_lb_target_group.app.arn
}