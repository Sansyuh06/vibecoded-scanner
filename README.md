# Vibe Scanner - Security Vulnerability Assessment Platform

A comprehensive security vulnerability scanning platform that automatically discovers and assesses security issues across web applications.

## 🎯 Features

- **Automated Web Crawling**: Respects SSL/TLS, robots.txt, and implements proper rate limiting
- **Multi-Plugin Architecture**: Extensible vulnerability check system
- **Comprehensive Security Checks**:
  - HTTP Security Headers Analysis
  - Authentication & Authorization Vulnerabilities
  - AI Agent Security Issues (Prompt Injection, Authority Escalation)
  - More plugins can be easily added
- **PDF Report Generation**: Professional security assessment reports
- **REST API**: Full-featured API for integration with other tools
- **Async Architecture**: Built on FastAPI + asyncio for high performance
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM with async support
- **PostgreSQL/SQLite**: Flexible database backend
- **Redis**: Caching and task queue
- **Celery**: Distributed task processing
- **Httpx**: HTTP client with retry logic

### Key Components

```
vibe_scanner/
├── api/                 # FastAPI routes and dependencies
├── db/                  # Database models and initialization
├── scanner/             # Core scanning engine
│   ├── crawler.py      # Smart web crawler
│   └── engine.py       # Orchestration engine
├── vulnerabilities/    # Pluggable vulnerability checks
│   ├── web/           # Web security checks
│   ├── auth/          # Authentication checks
│   └── ai/            # AI/LLM security checks
├── reporting/          # Report generation
└── config.py          # Configuration management
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (or use SQLite for development)
- Redis 7+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd vibecoded-scanner
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r vibe_scanner/requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Run the application**
```bash
uvicorn vibe_scanner.main:app --reload
```

### Docker Deployment

```bash
# Copy environment file
cp .env.example .env

# Build and run with Docker Compose
docker-compose up --build

# Application will be available at http://localhost:8000
# Frontend at http://localhost:3000
```

## 🔒 Security Features

### Critical Security Improvements
- ✅ **No Hardcoded Secrets**: All secrets loaded from environment variables
- ✅ **SSL/TLS Verification**: Enabled by default with proper certificate validation
- ✅ **SSRF Protection**: Input validation prevents scanning private IP ranges
- ✅ **Request Context Tracking**: All requests tracked with unique IDs
- ✅ **Rate Limiting**: Prevents abuse and DoS attacks
- ✅ **Comprehensive Logging**: Full audit trail of all operations
- ✅ **Error Handling**: Specific exception types for better diagnostics
- ✅ **Database Connection Pooling**: Optimized connection management

### Configuration Security

The application enforces security best practices:
- Minimum 32-character SECRET_KEY (enforced at startup)
- Short-lived access tokens (15 minutes default)
- Refresh token mechanism for long sessions
- Environment-specific validation

## 📋 API Documentation

### Interactive Docs
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Key Endpoints

#### Health Check
```
GET /health
GET /
```

#### Create Scan
```
POST /api/v1/scans/
{
  "target_url": "https://example.com"
}
```

#### Get Scans
```
GET /api/v1/scans/?skip=0&limit=10
```

#### Get Scan Details
```
GET /api/v1/scans/{scan_id}
```

#### Download PDF Report
```
GET /api/v1/scans/{scan_id}/report/pdf
```

## 🧩 Extending with Custom Checks

### Creating a Custom Vulnerability Check

```python
from vibe_scanner.vulnerabilities.base import VulnerabilityCheck, ScanContext, VulnerabilityIssue
from typing import List

class CustomSecurityCheck(VulnerabilityCheck):
    name = "Custom Security Check"
    category = "Custom Category"
    severity = "HIGH"
    description = "Checks for custom security issues"
    
    async def run(self, context: ScanContext) -> List[VulnerabilityIssue]:
        findings = []
        
        # Your security check logic here
        if some_vulnerability_found:
            findings.append(VulnerabilityIssue(
                name="Vulnerability Name",
                severity="HIGH",
                category="Custom Category",
                description="Detailed description",
                recommendation="How to fix it",
                location=context.target_url
            ))
        
        return findings
```

### Registering the Check

```python
# In routes.py or engine initialization
from .your_module import CustomSecurityCheck

# Register with scan engine
scan_engine.register_plugin(CustomSecurityCheck)
```

## 📊 Database Schema

### Tables
- **users**: User accounts and authentication
- **projects**: Collection of scans
- **scans**: Individual security assessments
- **findings**: Discovered vulnerabilities

## 🔧 Configuration

Environment variables (see `.env.example`):

```
# Security
SECRET_KEY=<generate-with-secrets-module>
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/vibedb
REDIS_URL=redis://localhost:6379/0

# Scanner
MAX_PAGES_TO_CRAWL=500
CRAWLER_TIMEOUT=10.0
CRAWLER_CONCURRENCY=10

# Logging
LOG_LEVEL=INFO
```

## 📝 Logging

Comprehensive logging includes:
- Request/response tracking with unique IDs
- Database operations
- Scan progress and findings
- Error stack traces
- Performance metrics

View logs:
```bash
# Development
tail -f logs/app.log

# Docker
docker logs vibe-scanner-api
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=vibe_scanner
```

## 📈 Performance Considerations

- Database connection pooling (10 connections, 20 overflow)
- Query optimization with selectinload for relationships
- Async I/O for all operations
- Efficient crawler with rate limiting and retry logic
- Redis caching for frequently accessed data

## 🐛 Error Handling

The application implements specific exception handling:
- `ScanEngineError`: Base engine errors
- `ScanNotFoundError`: Scan doesn't exist
- `CrawlError`: Crawling failed
- `VulnerabilityCheckError`: Check execution failed

All errors are logged with full context and returned with unique request IDs for debugging.

## 📚 Best Practices Implemented

1. **Separation of Concerns**: Clear module separation
2. **Dependency Injection**: FastAPI dependency system
3. **Type Hints**: Full type annotations throughout
4. **Async/Await**: Non-blocking I/O
5. **Structured Logging**: Consistent log formatting
6. **Error Boundaries**: Specific exception handling
7. **Security First**: Input validation, SSL/TLS, SSRF protection
8. **Documentation**: Comprehensive docstrings
9. **Configuration Management**: Externalized settings
10. **Monitoring**: Request tracking and performance metrics

## 🔐 Security Checklist

- [x] No hardcoded secrets
- [x] SSL/TLS verification enabled
- [x] SSRF protection
- [x] Rate limiting
- [x] Input validation
- [x] SQL injection prevention (using ORM)
- [x] CORS configuration
- [x] Logging and monitoring
- [x] Error handling without info disclosure
- [x] Database connection security

## 📞 Support

For issues, feature requests, or security concerns:
1. Check existing documentation
2. Review logs for error details
3. Check API request IDs for tracing
4. Report security issues privately

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- FastAPI
- SQLAlchemy
- httpx
- BeautifulSoup4
- ReportLab
