# Security Backlog
 
## Epic 1: Authentication & Authorization
- [ ] Implement user registration with email verification
- [ ] Implement login with bcrypt password hashing
- [ ] Add MFA using TOTP (Google Authenticator)
- [ ] Create IAM roles with least privilege
- [ ] Implement JWT-based sessions (15min expiration)
 
## Epic 2: Data Protection
- [ ] Enable S3 default encryption
- [ ] Enable RDS encryption
- [ ] Configure HTTPS-only ALB listener
- [ ] Store secrets in Secrets Manager
- [ ] Implement S3 Block Public Access
 
## Epic 3: Network Security
- [ ] Deploy VPC with public/private subnets
- [ ] Configure security groups (least privilege)
- [ ] Deploy database in private subnet
- [ ] Enable VPC Flow Logs
- [ ] Configure Network ACLs
 
## Epic 4: Monitoring & Incident Response
- [ ] Enable CloudTrail in all regions
- [ ] Enable GuardDuty
- [ ] Configure CloudWatch Alarms (unauthorized API calls, root usage)
- [ ] Create incident response runbook
- [ ] Set up SNS alerts for critical findings
 
## Epic 5: Compliance & Auditing
- [ ] Enable Security Hub with CIS Benchmark
- [ ] Create compliance matrix
- [ ] Automate evidence collection
- [ ] Document security controls
- [ ] Prepare for demo presentation
 
## Epic 6: Security Testing
- [ ] Run Prowler security assessment
- [ ] Scan Docker images with Trivy
- [ ] Conduct OWASP ZAP scan
- [ ] Perform manual security review
- [ ] Document findings and remediations