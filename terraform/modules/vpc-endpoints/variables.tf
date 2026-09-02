variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "capstone-project"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "data_route_table_id" {
  description = "Private Rout Table IDs where the data resides"
  type        = string
}