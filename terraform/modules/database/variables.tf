variable "table_name" {
  type = string
}

variable "hash_key" {
  type = string
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
  type = map(string)
  default = {
    Role = "database"
  }
}

variable "range_key" {
  type    = string
  default = null
}

variable "enable_ttl" {
  type    = bool
  default = false
}

variable "global_secondary_index" {
  type = object({
    name      = string
    hash_key  = string
    range_key = string
  })
  default = null
}