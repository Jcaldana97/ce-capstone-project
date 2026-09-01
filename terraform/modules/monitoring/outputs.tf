output "application_log_group_name" {
  description = "CloudWatch Log Group for the application API"
  value       = aws_cloudwatch_log_group.application.name
}

output "application_log_group_arn" {
  description = "ARN of the application API CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.application.arn
}