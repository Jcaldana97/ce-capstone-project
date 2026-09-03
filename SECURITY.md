# Security 

## Security controls implemented

- Creation of IAM Roles to allow access to certain resources to interact with other resources inside the network. 
- Creation of Security Groups to implement a least-priviledge approach for the communication between tiers and user. 

## Compliance frameworks addressed


## IAM roles and policies

### Roles

- **capstone-project-app-role**: Gives the application EC2 instances permission to access AWS services such as S3, CloudWatch, DynamoDB, and Systems Manager

### Custom Policies

- **capstone-project-app_s3**: Allows the EC2 application servers to download/read objects from the application's S3 bucket.
- **capstone-project-app-cloudwatch-logs**: Allows the EC2 instances/CloudWatch Agent to create CloudWatch log groups and streams and send application/system logs to CloudWatch Logs.
- **capstone-project-app-cloudwatch-metrics**: Allows the application/CloudWatch Agent to publish custom metrics to Amazon CloudWatch.
- **capstone-project-dynamodb-access**: Allows the Flask application running on EC2 to read and modify data in DynamoDB carts and metrics tables.

### AWS Managed Policies

- **AmazonSSMManagedInstanceCore**: Allows AWS Systems Manager (SSM) to manage your EC2 instances. This is what enables to connect/manage the instances through SSM rather than needing SSH access.

### Instance Profile

- **aws_instance_profile.app**

## Network security strategy

### capstone-project-alb-sg

| Direction | Port | Source / Destination | Purpose |
|-----------|------|----------------------|---------|
| Inbound | 80 | 0.0.0.0/0 | Public HTTP (internet-facing) |
| Outbound | All | 0.0.0.0/0 | Package downloads |

### capstone-project-app-sg

| Direction | Port | Source / Destination | Purpose |
|-----------|------|----------------------|---------|
| Inbound | 80 | capstone-project-alb-sg | App traffic from ALB |
| Outbound | All | 0.0.0.0/0 | Package downloads |

### capstone-project-data-sg

| Direction | Port | Source / Destination | Purpose |
|-----------|------|----------------------|---------|
| Inbound | 3306 | capstone-project-app-sg | MySQL from app tier only |
| Outbound | All | 0.0.0.0/0 | Package downloads |

### capstone-project-ssm-endpoint-sg
| Direction | Port | Source / Destination | Purpose |
|-----------|------|----------------------|---------|
| Inbound | HTTPS | capstone-project-app-sg | Communication to app tier |
| Outbound | All | 0.0.0.0/0 | Package downloads |


![Security Groups](docs/architecture/security-groups.png)

- Database can only receive requests from application tier. 
- Application tier does not listen directly to the internet (remains private) 
- Only Application Load Balancer can send requests which come from the internet.
- AWS Session Manager is only allowed to access the instances in app tier.

## Secrets management approach

Usage of GitHub secrets to store AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to allow Git to perform actions on AWS using terraform code. 

## Security testing results


## Known risks and mitigations


| Risk	                                         | Observation	                      | Severity	   | Mitigation | 
|------------------------------------------------|-----------------------------------|--------------|------------|
| **Policies not in least-privilege compliance** | CloudWatch Logs policy (arn:aws:logs:*:*:*) and the DynamoDB policy, which could potentially be narrowed further to exactly the resources/actions the application needs	                      | Medium	   | Update Policies to allow only the exactly resources needed |
| **HTTP rather than HTTPS** | Load balancer configuration includes an HTTP listener | High	   | Add an ACM certificate and HTTPS listener on port 443. Redirect HTTP → HTTPS |
| **S3 permissions could be tightened** | Application role has s3:GetObject against the bucket's objects | Medium | Restrict it to the exact object prefix the application needs and explicitly deny unintended access if appropriate |
| **EC2 metadata service** | No IMDSv2 enforcement in the launch template  | Medium | Require IMDSv2 with http_tokens = "required" |
| **No explicit WAF protection** | The public ALB is an obvious application attack surface | Medium | Add AWS WAF to the ALB, particularly if this is intended to resemble production infrastructure. |



