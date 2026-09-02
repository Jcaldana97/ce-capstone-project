locals {
  application_metrics = {
    tickets_sold_so_far = {
      filter_pattern = "\"TicketsSoldSoFar\""
      metric_name    = "TicketsSoldSoFar"
      metric_value   = "1"
    }

    completed_orders = {
      filter_pattern = "\"CompletedOrders\""
      metric_name    = "CompletedOrders"
      metric_value   = "1"
    }

    cancelled_orders = {
      filter_pattern = "\"CancelledOrders\""
      metric_name    = "CancelledOrders"
      metric_value   = "1"
    }

    cart_abandonment_rate = {
      filter_pattern = "\"CartAbandonmentRate\""
      metric_name    = "CartAbandonmentRate"
      metric_value   = "1"
    }

    tickets_sold_by_band = {
      filter_pattern = "\"TicketsSoldByBand\""
      metric_name    = "TicketsSoldByBand"
      metric_value   = "1"
    }

    tickets_sold_by_band_and_zone = {
      filter_pattern = "\"TicketsSoldByBandAndZone\""
      metric_name    = "TicketsSoldByBandAndZone"
      metric_value   = "1"
    }
  }
}

locals {
  technical_dashboard_body = templatefile(
    "./dashboards/technical-dashboard.json",
    {
      aws_region              = var.aws_region
      alb_arn_suffix          = var.alb_arn_suffix
      target_group_arn_suffix = var.target_group_arn_suffix
      autoscaling_group_name  = var.autoscaling_group_name
    }
  )
}

locals {
  business_dashboard_body = templatefile(
    "./dashboards/business-dashboard.json",
    {
      aws_region = var.aws_region
    }
  )
}

# Log Group Creation 
resource "aws_cloudwatch_log_group" "application" {
  name              = var.application_log_group_name
  retention_in_days = 30

  tags = {
    Name        = var.application_log_group_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Custom Metrics
resource "aws_cloudwatch_log_metric_filter" "application" {
  for_each = local.application_metrics

  name           = "${each.key}-filter"
  log_group_name = var.application_log_group_name
  pattern        = each.value.filter_pattern

  metric_transformation {
    name      = each.value.metric_name
    namespace = var.metric_namespace
    value     = each.value.metric_value
  }
}

# Dashboards creation
resource "aws_cloudwatch_dashboard" "application" {
  dashboard_name = "CapstoneTechnicalDashboard"

  dashboard_body = local.technical_dashboard_body
}

resource "aws_cloudwatch_dashboard" "application" {
  dashboard_name = "CapstoneBusinessDashboard"

  dashboard_body = local.business_dashboard_body
}