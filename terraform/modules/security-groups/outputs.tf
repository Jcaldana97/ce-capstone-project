output "alb_security_group_id" {
  description = "ALB Security Group ID"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "App Security Group ID"
  value       = aws_security_group.app.id
}

output "data_security_group_id" {
  description = "Data Security Group ID"
  value       = aws_security_group.data.id
}