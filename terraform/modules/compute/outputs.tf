output "app_instance_ids" {
  description = "App instance IDs"
  value       = aws_instance.app[*].id
}