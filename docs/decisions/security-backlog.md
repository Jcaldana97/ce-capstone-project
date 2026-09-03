# Security Backlog
 
## Epic 1: Authentication & Authorization
- [x] Implement user registration with email verification
- [ ] Implement login with bcrypt password hashing
- [x] Add MFA using TOTP (Google Authenticator)
- [x] Create IAM roles with least privilege
- [ ] Implement JWT-based sessions (15min expiration)
 
## Epic 2: Data Protection
- [x] Enable S3 default encryption
- [ ] Enable RDS encryption
- [ ] Configure HTTPS-only ALB listener
- [x] Store secrets in Secrets Manager
- [x] Implement S3 Block Public Access
 
## Epic 3: Network Security
- [x] Deploy VPC with public/private subnets
- [x] Configure security groups (least privilege)
- [x] Deploy database in private subnet
- [ ] Enable VPC Flow Logs
- [ ] Configure Network ACLs
 
## Epic 4: Monitoring & Incident Response
- [ ] Enable CloudTrail in all regions
- [ ] Enable GuardDuty
- [ ] Configure CloudWatch Alarms (unauthorized API calls, root usage)
- [x] Create incident response runbook
- [x] Set up SNS alerts for critical findings
 
## Epic 5: Compliance & Auditing
- [x] Enable TfSec and Trivy for Security Scanning
- [x] Create compliance matrix
- [ ] Automate evidence collection
- [x] Document security controls
- [x] Prepare for demo presentation
 
## Epic 6: Security Testing
- [ ] Run Prowler security assessment
- [ ] Scan Docker images with Trivy
- [ ] Conduct OWASP ZAP scan
- [ ] Perform manual security review
- [x] Document findings and remediations