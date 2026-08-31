output "app_autoscaling_group_name" {
  description = "Name of the application Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}

output "app_autoscaling_group_arn" {
  description = "ARN of the application Auto Scaling Group"
  value       = aws_autoscaling_group.app.arn
}

output "app_min_size" {
  description = "Minimum number of application instances"
  value       = aws_autoscaling_group.app.min_size
}

output "app_max_size" {
  description = "Maximum number of application instances"
  value       = aws_autoscaling_group.app.max_size
}