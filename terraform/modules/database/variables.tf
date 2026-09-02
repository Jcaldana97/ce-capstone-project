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

variable "hash_key" {
  type    = string
  default = "cart_id"
}

variable "billing_mode" {
  type    = string
  default = "PAY_PER_REQUEST"
}


variable "ttl_attribute" {
  type    = string
  default = "ttl"
}

variable "tags" {
  type    = map(string)
  default = {}
}