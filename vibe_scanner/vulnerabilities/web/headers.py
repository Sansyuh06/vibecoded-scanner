from typing import List
from ..base import VulnerabilityCheck, ScanContext, VulnerabilityIssue

class SecurityHeadersCheck(VulnerabilityCheck):
    name = "Security Headers Analysis"
    severity = "MEDIUM"
    category = "Web Security"
    description = "Checks for the presence of recommended security headers."

    # Each header with detailed CVE, description, and remediation
    HEADER_CHECKS = {
        'Strict-Transport-Security': {
            'severity': 'HIGH',
            'cve': 'CWE-319',
            'title': 'Missing HTTP Strict Transport Security (HSTS)',
            'description': 'The Strict-Transport-Security header is not set. This allows attackers to perform SSL stripping attacks, downgrading HTTPS connections to HTTP and intercepting sensitive data.',
            'recommendation': 'Add the following header to your server configuration: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload. For Apache: Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains". For Nginx: add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
            'references': ['https://owasp.org/www-project-secure-headers/', 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security']
        },
        'X-Content-Type-Options': {
            'severity': 'MEDIUM',
            'cve': 'CWE-16',
            'title': 'Missing X-Content-Type-Options Header',
            'description': 'The X-Content-Type-Options header is not set to "nosniff". This allows browsers to MIME-sniff responses, potentially executing malicious scripts disguised as other content types.',
            'recommendation': 'Add the header: X-Content-Type-Options: nosniff. For Apache: Header always set X-Content-Type-Options "nosniff". For Nginx: add_header X-Content-Type-Options "nosniff" always;',
            'references': ['https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options']
        },
        'X-Frame-Options': {
            'severity': 'MEDIUM',
            'cve': 'CWE-1021',
            'title': 'Missing X-Frame-Options (Clickjacking Protection)',
            'description': 'The X-Frame-Options header is missing. This vulnerability allows attackers to embed your site in an iframe and perform clickjacking attacks, tricking users into clicking hidden elements.',
            'recommendation': 'Add the header: X-Frame-Options: DENY or X-Frame-Options: SAMEORIGIN. For Apache: Header always set X-Frame-Options "SAMEORIGIN". For Nginx: add_header X-Frame-Options "SAMEORIGIN" always;',
            'references': ['https://owasp.org/www-community/attacks/Clickjacking', 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options']
        },
        'Content-Security-Policy': {
            'severity': 'HIGH',
            'cve': 'CWE-79',
            'title': 'Missing Content Security Policy (CSP)',
            'description': 'No Content-Security-Policy header detected. CSP is a critical defense against XSS attacks, data injection, and unauthorized script execution. Without CSP, your site is vulnerable to script injection attacks.',
            'recommendation': "Implement a strict CSP. Start with: Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; Gradually tighten the policy based on your application needs.",
            'references': ['https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP', 'https://csp-evaluator.withgoogle.com/']
        },
        'X-XSS-Protection': {
            'severity': 'LOW',
            'cve': 'CWE-79',
            'title': 'Missing X-XSS-Protection Header',
            'description': 'The X-XSS-Protection header is not set. While deprecated in modern browsers in favor of CSP, it still provides protection for older browsers against reflected XSS attacks.',
            'recommendation': 'Add the header: X-XSS-Protection: 1; mode=block. Note: This header is deprecated. Prioritize implementing Content-Security-Policy instead.',
            'references': ['https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection']
        },
        'Referrer-Policy': {
            'severity': 'LOW',
            'cve': 'CWE-200',
            'title': 'Missing Referrer-Policy Header',
            'description': 'The Referrer-Policy header is not configured. This may leak sensitive URL information to third-party sites through the Referer header.',
            'recommendation': 'Add the header: Referrer-Policy: strict-origin-when-cross-origin or Referrer-Policy: no-referrer for maximum privacy.',
            'references': ['https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy']
        },
        'Permissions-Policy': {
            'severity': 'LOW',
            'cve': 'CWE-16',
            'title': 'Missing Permissions-Policy Header',
            'description': 'The Permissions-Policy (formerly Feature-Policy) header is not set. This header allows you to control which browser features can be used, reducing attack surface.',
            'recommendation': 'Add the header: Permissions-Policy: geolocation=(), camera=(), microphone=() to disable unused browser features.',
            'references': ['https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy']
        }
    }

    async def run(self, context: ScanContext) -> List[VulnerabilityIssue]:
        findings = []
        response_headers = context.session.headers

        for header, check_data in self.HEADER_CHECKS.items():
            if header not in response_headers:
                findings.append(VulnerabilityIssue(
                    name=check_data['title'],
                    severity=check_data['severity'],
                    category="Security Headers",
                    description=check_data['description'],
                    evidence={
                        "missing_header": header,
                        "cve_cwe": check_data['cve'],
                        "references": check_data['references']
                    },
                    recommendation=check_data['recommendation'],
                    location=context.target_url
                ))
        return findings
