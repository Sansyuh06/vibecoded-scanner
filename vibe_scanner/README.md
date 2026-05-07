# Vibe Scanner - Production-Ready Security Platform

Vibe Scanner is a modular, scalable vulnerability scanner designed for modern AI and Vibe-Coded platforms.

## Features

- **Smart Crawling**: Async crawler with depth limits and domain scoping.
- **Vulnerability Plugins**: Extensible architecture for adding new checks.
  - **Standard Web**: Security headers, CORS, Secrets.
  - **AI/LLM**: Prompt Injection surface detection, Agent Authority Escalation.
- **Reporting**: Professional PDF reports.
- **API First**: Fully controllable via REST API.

## Installation

### Prerequisites
- Docker and Docker Compose

### Running with Docker

1. **Build and Start**:
   ```bash
   docker-compose up --build
   ```

2. **Access API Docs**:
   Go to `http://localhost:8000/api/v1/docs`

## Usage

### 1. Start a Scan
```bash
curl -X POST "http://localhost:8000/api/v1/scans/" \
     -H "Content-Type: application/json" \
     -d '{"target_url": "http://example.com"}'
```
Response:
```json
{"id": "scan_uuid", "status": "pending"}
```

### 2. Check Status
```bash
curl "http://localhost:8000/api/v1/scans/{scan_uuid}"
```

### 3. Get PDF Report
```bash
curl -O "http://localhost:8000/api/v1/scans/{scan_uuid}/report/pdf"
```

## Development

- **Backend**: FastAPI
- **Database**: PostgreSQL (Async)
- **Task Queue**: Celery (Optional for heavy loads)
