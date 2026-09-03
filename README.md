# Capstone Project: Production-Ready Cloud Platform

## Architecture overview and description 

The general overview of the architecture can be seen in the following picture: 

![Architecture](docs/architecture/architecture.png)

The main components can be described as follows: 
- **VPC**: The container of the network infrastructure. The purpose is to hold the subnets and network components of the system. 
- **ALB**: Responsible for forwarding the requests to the servers attached to the target groups that belongs to the ALB. As a complementary purpose, it monitors the instances attached and sends metrics to CloudWatch. 
- **NAT Gateway**: Allows outbound communication to the internet for private app subnets. It allows the instances to download packages needed for the execution of the application. 
- **Internet Gateway**: Allows the internet access to the VPC. This is the gateway between internet and all components of the VPC. 
- **Web Servers**: Instances that hold the application to execute and handle the requests coming from the ALB. 
- **Database**: Stores data managed by the application in a safe storage. 
- **CloudWatch Alerts**: Trigger alarms in case of an inconsistency on the network. 
- **CloudWatch Dashboards**: Allows the real-time monitoring of the network and business behavior.

## Prerequisites and setup instructions

- Create an S3 bucket for the storage of the backend tfstate file to allow remote state. 
- Create an IAM User with Administrator Access to allow resource creation. 
- Terraform installed. 
- Git repository with CI/CD Pipeline to automate resource planning and implementation. 
- Configure SSM Manager for debugging purposes. 
- Configure GitHub Secrets to store credential to allow Git to automate infrastructure creation process. 

## Deployment guide

- Design Architecture (Networking, Security Groups, Resource Definition, Monitoring and Alerting)
- Infrastructure as Code - Modular Approach
  - ALB
  - Compute (Application, Autoscaling Group, EC2 roles)
  - Database 
  - Monitoring (Alerts, Metrics and Dashboards)
  - Networking (VPC, Subnets, Route Tables)
  - Security Groups
  - VPC Endpoints
- Call modules in root main file to create the resources. 
- Deployment automated: plan and apply in CI/CD Pipeline
- Final UI accessible in the link: 

```
http://capstone-project-alb-931963269.us-east-1.elb.amazonaws.com/ui
```

## Testing instructions


## Cost summary

| Service                        | Quantity |  Monthly Cost (USD) |
|--------------------------------|----------|---------------------|
| VPC	                           | 1        |  $0                 |
| Internet Gateway	             | 1        |  $0                 |
| Subnets					               | 6 		    |  $0                 |
| Route Tables	                 | 3        |  $0                 |
| EC2 t3.micro instances	       | 3        |  $22.776            |
| EC2 EBS gp3 storage	           | 3        |  $1.92              |
| Application Load Balancer	     | 1        |  $16.43             |
| NAT Gateway hourly cost	       | 1        |  $32.85             |
| NAT Gateway data processing    | 100 GB   |  $4.50              |
| VPC Endpoints                  | 3        |  $30                |
| Dynamo DB Tables        	     | 3        |  $6                 |
| S3 Bucket                      | 1        |  $1                 |
| CloudWatch              	     | NA       |  $5                 |

**Total monthly cost :** ~$120.5 USD 

## Contact/attribution

Project author: Julio Cesar Aldana Almanza
Email: jcaldana97@gmail.com
Linked-In: https://www.linkedin.com/in/julio-aldana-almanza/