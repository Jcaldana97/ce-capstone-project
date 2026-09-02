# Create VPC Endpoint for DynamoDB

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [var.data_route_table_id]

  tags = {
    Name = "${var.project_name}-dynamodb-endpoint"
  }
}