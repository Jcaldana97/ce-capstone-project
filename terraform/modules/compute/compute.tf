data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "app" {
  count = var.app_instance_count

  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t3.micro"
  subnet_id              = var.app_subnet_cidrs[count.index % length(var.app_subnet_cidrs)] != "" ? aws_subnet.app[count.index % length(var.app_subnet_cidrs)].id : aws_subnet.app[0].id
  vpc_security_group_ids = [aws_security_group.app.id]
  key_name               = var.key_name

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
              AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
              cat > /var/www/html/index.html <<HTML
              <html>
              <head><title>Project 1 - Terraform</title></head>
              <body>
                <h1>Project 1 — Deployed with Terraform</h1>
                <p>Instance: $INSTANCE_ID</p>
                <p>AZ: $AZ</p>
              </body>
              </html>
              HTML
              EOF

  tags = {
    Name        = "${var.project_name}-app-${count.index + 1}"
    Environment = var.environment
    Role        = "app"
  }
}

resource "aws_lb_target_group_attachment" "app" {
  count            = var.app_instance_count
  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app[count.index].id
  port             = 80
}