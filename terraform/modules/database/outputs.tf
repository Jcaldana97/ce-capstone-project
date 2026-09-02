output "table_name" {
  value = aws_dynamodb_table.db.name
}

output "table_arn" {
  value = aws_dynamodb_table.db.arn
}