output "vpc_id" {
  description = "VPC identifier"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "app_subnet_ids" {
  description = "IDs of app subnets"
  value       = aws_subnet.app[*].id
}

output "data_subnet_ids" {
  description = "IDs of app subnets"
  value       = aws_subnet.app[*].id
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_id" {
  description = "IDs of NAT Gateway"
  value       = aws_nat_gateway.main.id
}

output "public_route_table_id" {
  description = "ID of public route table"
  value       = aws_route_table.public.id
}

output "app_route_table_id" {
  description = "ID of app route tables"
  value       = aws_route_table.app.id
}

output "data_route_table_id" {
  description = "ID of data route tables"
  value       = aws_route_table.data.id
}