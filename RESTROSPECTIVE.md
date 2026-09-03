# Retrospective

## What went well

- Application up and running, portable, connected to database and instrumenting metrics properly. 
- Terraform code builds a functional three-tier network
- CI/CD Automation properly implemented
- Security scans automatically run and generate reports. 
- Auto-Scaling group functional and properly reactive. 
- Technical & Business dashboards showing the required information for monitoring. 
- Alerts triggered and notifications sent to SNS recipient.  

## What challenges were faced

- Extending the application functionality cause an overhead in development time. 
- Instrument the metrics to send the proper values to be displayed in the dashboard.
- Data corruption due to Application Load Balancer switching between instances in the UI endpoint. 
- Troubleshooting application become harder due to network privacy and complexity

## How challenges were overcome

- Limit the application scope and use a powerful AI tool to help with code suggestions. 
- Application calls cloudwatch agent directly and send the already calculated values to the metrics used by the dashboards. 
- Implementation of a DynamoDB for storing and collecting data coming from the application.  
- Launch a testing instance for debugging purpose and configuration of application installation via S3 bucket. 

## Technical skills learned

- Create a complete Networking Infrastructure using modular approach with terraform
- Implement Auto-Scaling Group with a Database connected to the instances. 
- Select the approach that best handles instrumentation. 
- Use security tools to generate findings and establish compliance matrix. 

## What would you do differently

- Design the application and infrastructure carefully and consider the needs that each topic may have from the other. 
- Start by creating the functional final application might be an option. 
- Implement the CI/CD Pipeline automation with all the needed checks first. 

## Future improvements planned

- Eliminate wildcards from policies (target specific resources)
- Get ACM Certificate and enable secure HTTP protocol. 
- Remove unrestricted egress from security groups. 
- Enable WAF Protection to prevent ALB to be attacked. 
- Revisit terraform code for unused resources.