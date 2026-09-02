locals {
  base_attributes = concat(
    [{ name = var.hash_key, type = "S" }],
    var.range_key != null ? [{ name = var.range_key, type = "S" }] : [],
    var.global_secondary_index != null ? [
      { name = var.global_secondary_index.hash_key, type = "S" },
      { name = var.global_secondary_index.range_key, type = "N" }
    ] : []
  )

  unique_attributes = { for attr in local.base_attributes : attr.name => attr.type }
}

resource "aws_dynamodb_table" "db" {
  name         = var.table_name
  billing_mode = var.billing_mode
  hash_key     = var.hash_key
  range_key    = var.range_key

  dynamic "attribute" {
    for_each = local.unique_attributes
    content {
      name = attribute.key
      type = attribute.value
    }
  }

  dynamic "global_secondary_index" {
    for_each = var.global_secondary_index != null ? [var.global_secondary_index] : []
    content {
      name            = global_secondary_index.value.name
      hash_key        = global_secondary_index.value.hash_key
      range_key       = global_secondary_index.value.range_key
      projection_type = "ALL"
    }
  }

  ttl {
    attribute_name = var.ttl_attribute
    enabled        = var.enable_ttl
  }

  tags = var.tags
}