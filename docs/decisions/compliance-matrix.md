# TFSec & Trivy Compliance Matrix
 
| Control | Implementation | Evidence | Status | Owner | Priority |
|---------|----------------|----------|--------|-------|----------|
| No root user access key | Root account has no access keys | IAM Credential Report | ✅ Compliant | Security | - |
| MFA enabled for root user | Hardware MFA configured | IAM Account Summary | ✅ Compliant | Security | - |
| CloudWatch alarm for unauthorized API calls | Metric filter + SNS alarm | CloudWatch config | ✅ Compliant | Platform | High |
| Policies not in least-privilege compliance | Update Policies to allow only the exactly resources needed | IAM Account Summary | ⚠️ TODO | Platform | Medium |
| HTTP rather than HTTPS | Add an ACM certificate and HTTPS listener on port 443. Redirect HTTP → HTTPS | Config compliance report | ⚠️ TODO | Platform | Critical |
| S3 permissions could be tightened | Restrict it to the exact object prefix the application needs and explicitly deny unintended access if appropriate | S3 config report | ⚠️ TODO | Platform | Medium |
| EC2 metadata service | Require IMDSv2 with http_tokens = "required"  | Config compliance report | ❌ 3 violations | Platform | High |
| No explicit WAF protection | Add AWS WAF to the ALB, particularly if this is intended to resemble production infrastructure | Security | ❌ 1 violation  | Security | Critical |
| No security groups allow SSH from 0.0.0.0/0 | Config rule active | Config compliance report | ✅ Compliant | DevOps | Critical |
| No security groups allow RDP from 0.0.0.0/0 | Config rule active | Config compliance report | ✅ Compliant | DevOps | - |
| CloudTrail enabled in all regions | Multi-region trail active | CloudTrail config export |⚠️ TODO  | Platform | - |
| CloudTrail log file validation enabled | Log validation active | CloudTrail config | ⚠️ TODO | Platform | - |