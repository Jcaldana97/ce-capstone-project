variable "project_name" {
  description = "Project identifier"
  type        = string
}

variable "environment" {
  description = "project environment"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "app_instance_count" {
  description = "Number of app instances"
  type        = number
  default     = 3

  validation {
    condition     = var.app_instance_count >= 3
    error_message = "app_instance_count must be at least 3."
  }
}

variable "app_min_size" {
  description = "Minimum number of application instances"
  type        = number
  default     = 3
}

variable "app_max_size" {
  description = "Maximum number of application instances"
  type        = number
  default     = 6
}

variable "app_instance_type" {
  description = "EC2 instance type for application instances"
  type        = string
  default     = "t3.micro"
}

variable "app_cpu_target" {
  description = "Target average CPU utilization for application ASG"
  type        = number
  default     = 70
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "app_subnet_ids" {
  description = "Private Subnet ID where the app resides"
  type        = list(string)
}

variable "security_group_app_id" {
  description = "Security group of App Tier"
  type        = string
}

variable "alb_target_group_app_arn" {
  description = "ARN of the Target Group in the Load Balancer"
  type        = string
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
}

variable "security_group_ssm_endpoint_id" {
  description = "SSM VPC Endpoint Security Group"
  type        = string
}

variable "database_table_arn" {
  description = "ARN of DynamoDB Database table"
  type        = string
}


