variable "project_name" {
  description = "Project identifier"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "subscription_email" {
  description = "Recipient for SNS topic alerts"
  type        = string
  default     = "julioaldana.deu@gmail.com"
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix used by CloudWatch metrics"
  type        = string
}

variable "target_group_arn_suffix" {
  description = "Target group ARN suffix used by CloudWatch metrics"
  type        = string
}

variable "autoscaling_group_name" {
  description = "Auto Scaling Group name"
  type        = string
}

variable "cpu_threshold" {
  description = "CPU utilization alarm threshold"
  type        = number
  default     = 80
}

variable "unhealthy_host_threshold" {
  description = "Number of unhealthy hosts that triggers an alarm"
  type        = number
  default     = 1
}

variable "application_log_group_name" {
  description = "CloudWatch Log Group containing application.log entries"
  type        = string
  default     = "/capstone/application/api"
}

variable "metric_namespace" {
  description = "CloudWatch namespace for application metrics"
  type        = string
  default     = "Tickets/Application"
}