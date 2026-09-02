resource "aws_dynamodb_table" "db" {
  name         = "${var.project_name}-database"
  billing_mode = var.billing_mode
  hash_key     = var.hash_key

  attribute {
    name = var.hash_key
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "N"
  }

  global_secondary_index {
    name            = "status-updated_at-index"
    hash_key        = "status"
    range_key       = "updated_at"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = var.ttl_attribute
    enabled        = true
  }

  tags = var.tags
}

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