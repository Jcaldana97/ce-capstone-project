# Create SNS Topic and subscription 
resource "aws_sns_topic" "topic" {
  name = "topic-name"
}

resource "aws_sns_topic_subscription" "email-target" {
  topic_arn = aws_sns_topic.topic.arn
  protocol  = "email"
  endpoint  = var.subscription_email
}

# Alarm 1: High Error Rate

resource "aws_cloudwatch_metric_alarm" "alb_http_5xx" {
  alarm_name = "${var.project_name}-HighErrorRate"

  alarm_description = "ALB when error rate exceeds 10 per 5 minutes"

  namespace   = "AWS/ApplicationELB"
  metric_name = "HTTPCode_ELB_5XX_Count"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 2
  threshold           = 10
  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.topic.arn
  ]

  ok_actions = [
    aws_sns_topic.topic.arn
  ]
}

# Alarm 2: Unhealthy Targets

resource "aws_cloudwatch_metric_alarm" "unhealthy_targets" {
  alarm_name = "${var.project_name}-ALBUnhealthyTargets"

  alarm_description = "ALB has unhealthy targets"

  namespace   = "AWS/ApplicationELB"
  metric_name = "UnHealthyHostCount"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
    TargetGroup  = var.target_group_arn_suffix
  }

  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 3
  threshold           = var.unhealthy_host_threshold
  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]
}

# Alarm 3: High CPU utilization

resource "aws_cloudwatch_metric_alarm" "asg_cpu" {
  alarm_name = "${var.project_name}-ASGHighCpu"

  alarm_description = "Average ASG CPU utilization is too high"

  namespace   = "AWS/EC2"
  metric_name = "CPUUtilization"

  dimensions = {
    AutoScalingGroupName = var.autoscaling_group_name
  }

  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = var.cpu_threshold
  comparison_operator = "GreaterThanOrEqualToThreshold"

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  ok_actions = [
    aws_sns_topic.alerts.arn
  ]
}