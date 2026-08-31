variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "capstone-project"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.1.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "app_subnet_cidrs" {
  description = "Application subnet CIDRs"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "data_subnet_cidrs" {
  description = "Data subnet CIDRs"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

variable "app_instance_count" {
  description = "Number of app instances"
  type        = number
  default     = 3
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

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
  default     = "bootcamp-week2-key"
}