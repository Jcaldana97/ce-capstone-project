data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}


#
# Package the Flask application.
#
# Assumes the Terraform root module is run from the repository root
# and the application is located at ./app/src.
#
data "archive_file" "app" {
  type        = "zip"
  source_dir  = "${path.root}/../app/src"
  output_path = "${path.root}/../app.zip"
}


resource "aws_s3_bucket" "app" {
  bucket = "${var.project_name}-app-julioaldana"

  tags = {
    Name        = "${var.project_name}-app-julioaldana"
    Environment = var.environment
  }
}

resource "aws_s3_object" "app" {
  bucket = aws_s3_bucket.app.id
  key    = "app.zip"
  source = data.archive_file.app.output_path

  etag = filemd5(data.archive_file.app.output_path)
}


#
# Launch Template
#
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-app-"
  image_id      = data.aws_ami.amazon_linux_2.id
  instance_type = var.app_instance_type
  key_name      = var.key_name

  iam_instance_profile {
    name = aws_iam_instance_profile.app.name
  }

  vpc_security_group_ids = [
    var.security_group_app_id
  ]

  user_data = base64encode(<<-EOF
    #!/bin/bash

    set -e

    # Update packages
    yum update -y

    # Instal SSM Agent
    yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm

    systemctl start amazon-ssm-agent

    # Download  
    wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
    
    # Install
    rpm -U ./amazon-cloudwatch-agent.rpm
    
    # Verify installation
    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status -m ec2

    # Install Python and required tools
    amazon-linux-extras enable python3.8
    yum clean metadata
    yum install -y python3.8 python3.8-pip unzip awscli

    # Create application directory
    mkdir -p /opt/app

    # Download application package
    aws s3 cp \
      s3://${aws_s3_bucket.app.bucket}/app.zip \
      /tmp/app.zip

    unzip -o /tmp/app.zip -d /opt/app

    # Configure and Run CloudWatch Agent
    mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/
    nano /opt/aws/amazon-cloudwatch-agent/etc/config.json

    cp /opt/app/config/cloudwatch-agent-config.json /opt/aws/amazon-cloudwatch-agent/etc/config.json

    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
    
    # Create Python virtual environment
    python3.8 -m venv /opt/app/venv

    # Install Python dependencies
    /opt/app/venv/bin/pip install --upgrade pip
    /opt/app/venv/bin/pip install -r /opt/app/requirements.txt
    /opt/app/venv/bin/pip install gunicorn

    # Create systemd service
    cat > /etc/systemd/system/flask-app.service <<SERVICE
    [Unit]
    Description=Flask Application
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/opt/app
    Environment="PATH=/opt/app/venv/bin"
    ExecStart=/opt/app/venv/bin/gunicorn --bind 0.0.0.0:80 --workers 2 app:app
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    SERVICE

    # Start Flask application
    systemctl daemon-reload
    systemctl enable flask-app
    systemctl start flask-app

  EOF
  )

  tag_specifications {
    resource_type = "instance"

    tags = {
      Name        = "${var.project_name}-app"
      Environment = var.environment
      Role        = "app"
    }
  }

  tag_specifications {
    resource_type = "volume"

    tags = {
      Name        = "${var.project_name}-app"
      Environment = var.environment
      Role        = "app"
    }
  }
}

#
# Auto Scaling Group
#
resource "aws_autoscaling_group" "app" {
  name = "${var.project_name}-app-asg"

  min_size         = var.app_min_size
  max_size         = var.app_max_size
  desired_capacity = var.app_instance_count

  vpc_zone_identifier = var.app_subnet_ids

  health_check_type         = "ELB"
  health_check_grace_period = 300

  target_group_arns = [
    var.alb_target_group_app_arn
  ]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-app"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = var.environment
    propagate_at_launch = true
  }

  tag {
    key                 = "Role"
    value               = "app"
    propagate_at_launch = true
  }
}

#
# CPU-based scaling
#
resource "aws_autoscaling_policy" "app" {
  name                   = "${var.project_name}-app-cpu-scaling"
  autoscaling_group_name = aws_autoscaling_group.app.name

  policy_type = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }

    target_value = var.app_cpu_target
  }
}