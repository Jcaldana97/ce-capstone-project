variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "capstone-project"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "security_group_alb_id" {
  description = "Security Group ID of ALB"
  type        = string
}

variable "alb_public_subnet_id" {
  description = "Public Subnet ID where the ALB resides"
  type        = string
}

