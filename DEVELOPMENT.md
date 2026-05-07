# Development Guide

## Setup

### 1. Install Python 3.10+

```bash
python --version  # Should be 3.10 or higher
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r vibe_scanner/requirements.txt
```

### 4. Create Environment File

```bash
cp .env.example .env
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Update `.env` with the generated key and other settings.

### 5. Setup Database

For PostgreSQL:
```bash
# Make sure PostgreSQL is running
createdb vibedb
createuser vibe
# Update .env with correct DATABASE_URL
```

For SQLite (development):
```bash
# Already configured in .env.example
DATABASE_URL=sqlite+aiosqlite:///./vibe.db
```

### 6. Run Migrations

```bash
alembic upgrade head
```

### 7. Start Development Server

```bash
uvicorn vibe_scanner.main:app --reload --host 0.0.0.0 --port 8000
```

Access at: http://localhost:8000/api/v1/docs

## Docker Development

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## Code Structure

```
vibe_scanner/
├── api/                 # REST API endpoints
│   ├── routes.py       # API route handlers
│   └── dependencies.py # FastAPI dependencies
├── db/                 # Database layer
│   ├── database.py     # Connection and session management
│   └── models.py       # SQLAlchemy ORM models
├── scanner/            # Core scanning logic
│   ├── crawler.py      # Web crawler implementation
│   ├── engine.py       # Scan orchestration engine
│   └── worker.py       # Celery task workers
├── vulnerabilities/    # Security check plugins
│   ├── base.py         # Base check class
│   ├── web/            # Web security checks
│   ├── auth/           # Auth security checks
│   └── ai/             # AI/LLM security checks
├── reporting/          # Report generation
│   └── pdf.py          # PDF report generation
├── config.py           # Configuration management
└── main.py            # Application entry point
```

## Common Development Tasks

### Running Tests

```bash
pytest
pytest -v  # Verbose
pytest --cov=vibe_scanner  # With coverage
```

### Code Formatting

```bash
# Format code
black vibe_scanner/

# Check code style
flake8 vibe_scanner/
pylint vibe_scanner/
```

### Type Checking

```bash
mypy vibe_scanner/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of change"

# Review the migration in alembic/versions/
# Then apply it
alembic upgrade head
```

### Creating a New Vulnerability Check

1. Create file in `vibe_scanner/vulnerabilities/{category}/{check_name}.py`
2. Implement the check class:

```python
from vibe_scanner.vulnerabilities.base import VulnerabilityCheck, ScanContext, VulnerabilityIssue
from typing import List

class MySecurityCheck(VulnerabilityCheck):
    name = "My Security Check"
    category = "Custom"
    severity = "HIGH"
    description = "Checks for specific security issues"
    
    async def run(self, context: ScanContext) -> List[VulnerabilityIssue]:
        findings = []
        
        # Implement your check logic
        # Access: context.target_url, context.session (httpx.Response), context.soup (BeautifulSoup)
        
        if vulnerability_found:
            findings.append(VulnerabilityIssue(
                name="Issue Name",
                severity="HIGH",
                category="Custom",
                description="What the issue is",
                recommendation="How to fix it",
                location=context.target_url,
                evidence={"details": "any metadata"}
            ))
        
        return findings
```

3. Register in `vibe_scanner/api/routes.py`:

```python
from ..vulnerabilities.custom.my_check import MySecurityCheck

# In run_scan_background():
scan_engine.register_plugin(MySecurityCheck)
```

## Debugging

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG

# Or run with:
ENVIRONMENT=development DEBUG=true uvicorn vibe_scanner.main:app --reload
```

### Using a Debugger

```bash
# With pdb
python -m pdb -m uvicorn vibe_scanner.main:app

# With VS Code debugger - create .vscode/launch.json:
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["vibe_scanner.main:app", "--reload"],
            "jinja": true
        }
    ]
}
```

### Check Database

```bash
# SQLite
sqlite3 vibe.db

# PostgreSQL
psql vibedb
```

Query examples:
```sql
-- View scans
SELECT id, target_url, status, created_at FROM scans ORDER BY created_at DESC LIMIT 10;

-- View findings
SELECT * FROM findings WHERE severity = 'CRITICAL' ORDER BY created_at DESC;

-- Count findings by severity
SELECT severity, COUNT(*) FROM findings GROUP BY severity;
```

## Performance Tuning

### Database Indexes

Key indexes are defined in models.py. For custom queries, consider adding:

```python
from sqlalchemy import Index

# In migration:
op.create_index('idx_scan_status_created', 'scans', ['status', 'created_at'], unique=False)
```

### Cache Configuration

Redis is used for:
- Celery task queue
- Session storage
- Result caching

### Connection Pooling

For PostgreSQL, adjust in config.py:
```python
pool_size=20  # Increase for more concurrent connections
max_overflow=40  # Overflow connections
```

## Deployment

### Production Checklist

- [ ] Generate secure SECRET_KEY
- [ ] Set ENVIRONMENT=production
- [ ] Set DEBUG=false
- [ ] Configure proper DATABASE_URL (PostgreSQL)
- [ ] Configure REDIS_URL
- [ ] Set up CORS_ORIGINS properly
- [ ] Enable HTTPS/SSL
- [ ] Configure logging and monitoring
- [ ] Set up rate limiting
- [ ] Configure backup strategy
- [ ] Set up health checks
- [ ] Configure auto-restart

### Environment Variables

```bash
# Production
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<very-secure-key>
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://host:6379/0
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com"]
```

### Monitoring

Monitor these metrics:
- API response times
- Database query performance
- Scan completion rates
- Error rates by type
- Redis memory usage
- Worker task queue depth

## Troubleshooting

### Database Connection Errors

```
# Check database is running
# Check DATABASE_URL is correct
# Check credentials
# For PostgreSQL: psql -U user -h host -d vibedb
```

### SSL/TLS Certificate Errors

```
# Development: the app validates SSL by default
# For self-signed certs in development, you need to:
# 1. Add cert to system trust store, OR
# 2. Temporarily disable SSL verification (development only)

# See crawler.py - verify=False for development workarounds
```

### Memory/Performance Issues

```bash
# Monitor resource usage
docker stats

# Check slow queries
# Enable query logging in config.py: echo=True
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Run code formatting
5. Commit with clear messages
6. Push and create PR

## Resources

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- OWASP Testing Guide: https://owasp.org/
- CWE Top 25: https://cwe.mitre.org/top25/
