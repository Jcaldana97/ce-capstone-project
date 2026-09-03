# Costs 

## Itemized monthly cost breakdown

| Service                        | Quantity | Calculation                       | Monthly Cost (USD) |
|--------------------------------|----------|-----------------------------------|--------------------|
| VPC	                           | 1        | 1 × $0/month                      | $0                 |
| Internet Gateway	             | 1        | 1 × $0/month	                    | $0                 |
| Subnets					               | 6 		    | 6 × $0/month	                    | $0                 |
| Route Tables	                 | 3        | 3 × $0/month	                    | $0                 |
| EC2 t3.micro instances	       | 3        | 3 × $0.0104/hr × 730 hrs	        | $22.776            |
| EC2 EBS gp3 storage	           | 3        | 3 × 8 GB × $0.08/GB-month         | $1.92              |
| Application Load Balancer	     | 1        | 1 × $0.0225/hr × 730 hrs	        | $16.43             |
| NAT Gateway hourly cost	       | 1        | 1 × $0.045/hr × 730 hrs	          | $32.85             |
| NAT Gateway data processing    | 100 GB   | 100 GB × $0.045/GB	              | $4.50              |
| VPC Endpoints                  | 3        | 3 x $10                           | $30                |
| Dynamo DB Tables        	     | 3        | 3 × $2	                          | $6                 |
| S3 Bucket                      | 1        | 1 x $1                            | $1                 |
| CloudWatch              	     | NA       | Included	                        | $5                 |

**Total monthly cost :** ~$120.5 USD      

## Cost optimization strategies

### Implemented

- Enable auto-scaling to launch only sufficient instances to keep the system working. 
- Add VPC Endpoints for services such as DynamoDB, Systems Manager, CloudWatch to reduce NAT Gateway usage.
- Enable Workload Optimization to reduce working hours of EC2 Instances.
- Optimize logging retention

## To be considered 
- Apply Saving Plans for stable EC2 workloads to reduce On-demand costs. 
- If acceptable for non-critical workloads, run a Single-AZ instance instead of Multi-AZ (roughly halves the RDS compute cost)
- Revisit instance sizes after collecting 30–60 days of CloudWatch metrics

## ROI analysis for optimizations

| Optimization	                     | Monthly Saving   | Annual Saving |Implementation Effort	| Risk   |
|------------------------------------|------------------|---------------|-----------------------| -------|
| Add VPC Endpoints	                 | $5–20	        | $60–240       | Low	                | Low    |
| Use Savings Plans	                 | $8–15	        | $96–180       | Low	                | Low    |
| Switch t3.micro → t4g.micro	     | $5–8	            | $60–96	    | Medium	            | Medium |
| Reserved DB Instance	             | $8–15	        | $96–180	    | Low	                | Low    |
| Remove idle EC2 instances	         | Variable	        | Variable	    | Medium	            | Medium |
| Use private service endpoints	     | $5–15	        | $60–180	    | Medium	            | Low    |
| Reduce logging noise	             | $5–10	        | $60–120	    | Medium	            | Low    |