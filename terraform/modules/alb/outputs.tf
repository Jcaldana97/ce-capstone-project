output "alb_dns_name" {
  description = "ALB DNS name — access your application here"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "Full URL for the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "alb_target_group_app_arn" {
  description = "ARN of the Target Group in the Load Balancer"
  value       = aws_lb_target_group.app.arn
}