# Capstone Threat Model (STRIDE)
 
## Assets
- User credentials (email, password)
- Customer PII (name, address, payment info)
- Application secrets (API keys, database credentials)
 
## Threats & Mitigations
 
### Spoofing
**Threat:** Attacker steals session cookie
- **Mitigation:** HttpOnly cookies, short-lived JWTs, MFA
- **Priority:** High
- **Backlog Item:** Implement secure session management
 
### Tampering
**Threat:** SQL injection modifies data
- **Mitigation:** Parameterized queries, WAF SQL injection rules
- **Priority:** Critical
- **Backlog Item:** Implement input validation and parameterized queries
 
### Repudiation
**Threat:** User denies action
- **Mitigation:** CloudTrail logs, application audit trail
- **Priority:** Medium
- **Backlog Item:** Enable CloudTrail and application logging
 
### Information Disclosure
**Threat:** S3 bucket exposes data
- **Mitigation:** Block Public Access, encryption, access logging
- **Priority:** Critical
- **Backlog Item:** Configure S3 security controls
 
### Denial of Service
**Threat:** DDoS attack
- **Mitigation:** AWS Shield, CloudFront, rate limiting
- **Priority:** Medium
- **Backlog Item:** Enable Shield and configure WAF
 
### Elevation of Privilege
**Threat:** ECS task role has admin access
- **Mitigation:** Least privilege IAM
- **Priority:** High
- **Backlog Item:** Create least-privilege IAM roles