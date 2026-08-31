variable "app_instance_count" {
  description = "Number of app instances"
  type        = number
  default     = 3
}

variable "app_subnet_cidrs" {
  description = "Application subnet CIDRs"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "app_subnet_ids" {
  description = "Public Subnet ID where the app resides"
  type        = list(string)
}

variable "security_group_app_id" {
  description = "Security group of App Tier"
  type        = string
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
}

variable "environment" {
  description = "project environment"
  type        = string
  default     = "dev"
}

variable "aws_lb_target_group_app_arn" {
  description = "ARN of the Target Group in the Load Balancer"
  type        = string
}