from typing import List
from ..base import VulnerabilityCheck, ScanContext, VulnerabilityIssue

class BasicAuthCheck(VulnerabilityCheck):
    name = "Authentication Security Analysis"
    severity = "CRITICAL"
    category = "Authentication"
    description = "Checks for authentication vulnerabilities and misconfigurations."

    async def run(self, context: ScanContext) -> List[VulnerabilityIssue]:
        findings = []
        url = context.target_url
        
        # Check for unauthenticated API access
        if "/api/" in url and context.session.status_code in [200, 201]:
            findings.append(VulnerabilityIssue(
                name="Broken Access Control - Unauthenticated API Endpoint",
                severity="CRITICAL",
                category="Authentication",
                description="The API endpoint returns a successful response (HTTP 200/201) without requiring authentication. This allows unauthenticated attackers to access potentially sensitive data or perform unauthorized actions. This is listed as #1 in the OWASP Top 10 2021.",
                evidence={
                    "status_code": context.session.status_code, 
                    "url": url,
                    "cve_cwe": "CWE-306",
                    "owasp": "A01:2021 – Broken Access Control"
                },
                recommendation="""1. Implement JWT or OAuth 2.0 authentication for all API endpoints.
2. Add authentication middleware that validates tokens before processing requests.
3. Return HTTP 401 Unauthorized for requests without valid credentials.
4. Implement rate limiting to prevent brute-force attacks.
5. Use HTTPS to encrypt authentication tokens in transit.

Example (Node.js/Express):
```javascript
app.use('/api/', authMiddleware);
```

Example (Python/FastAPI):
```python
@app.get("/api/resource")
async def get_resource(user: User = Depends(get_current_user)):
    return resource
```""",
                location=url
            ))
        
        # Check for missing authentication headers in response
        response_headers = context.session.headers
        if 'WWW-Authenticate' not in response_headers and '/admin' in url.lower():
            findings.append(VulnerabilityIssue(
                name="Missing Authentication Challenge on Admin Endpoint",
                severity="HIGH",
                category="Authentication",
                description="The administrative endpoint does not present an authentication challenge. This may indicate the admin panel is publicly accessible without proper access controls.",
                evidence={
                    "url": url,
                    "cve_cwe": "CWE-287",
                    "owasp": "A07:2021 – Identification and Authentication Failures"
                },
                recommendation="""1. Protect admin endpoints with strong authentication (MFA recommended).
2. Implement IP whitelisting for administrative access.
3. Use separate domains or network segments for admin interfaces.
4. Enable audit logging for all admin actions.
5. Implement session timeout for administrative sessions.""",
                location=url
            ))
        
        return findings
