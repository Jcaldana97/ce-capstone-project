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