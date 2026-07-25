# AI Module Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd d:\backend
pip install -r requirements.txt
```

The following packages are included:
- `google-generativeai==0.8.3` - Gemini API integration
- `pydantic==2.10.3` - Request/response validation
- `sqlalchemy==2.0.36` - Database ORM
- `fastapi==0.115.6` - Web framework

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
GEMINI_API_KEY=your-api-key-from-google-cloud

# Database (required)
DATABASE_URL=postgresql://user:password@localhost:5432/schoolai

# JWT (required)
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging (optional)
LOG_LEVEL=INFO
```

### 3. Obtain Gemini API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Generative AI API**
4. Create an API key (not OAuth):
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **API Key**
5. Copy the key to `.env` file
6. (Optional) Restrict to `generativelanguage.googleapis.com`

### 4. Start the Application

```bash
# Development
python main.py

# Or with Uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Verify AI Module

```bash
# Check health endpoint
curl http://localhost:8000/health

# Should show:
# {
#   "status": "ok",
#   "ai_module": "ready",
#   "gemini_configured": true,
#   "fallback_mode": false
# }
```

---

## Detailed Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ❌ No | `""` | Google Gemini API key. Leave empty for fallback mode. |
| `DATABASE_URL` | ✅ Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | ✅ Yes | - | JWT signing secret (min 32 chars recommended) |
| `ALGORITHM` | ❌ No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ No | `30` | JWT token expiration |
| `LOG_LEVEL` | ❌ No | `INFO` | Python logging level (DEBUG, INFO, WARNING, ERROR) |

### Database Connection String Format

**PostgreSQL** (recommended for production):
```
postgresql://username:password@localhost:5432/schoolai_db
```

**PostgreSQL with connection pooling** (production):
```
postgresql://username:password@localhost:5432/schoolai_db?sslmode=require
```

### JWT Configuration

```python
# Example: Strong SECRET_KEY generation
import secrets
secrets.token_urlsafe(32)  # Run in Python to generate

# Output example:
# s8_Q-kNzZ7H0lJp3R-mB4vL2Q9tXyW5a6b8cDeFgH7i
```

---

## Deployment Scenarios

### Scenario 1: Development (Without Gemini)

```bash
# Start without API key - fallback mode active
GEMINI_API_KEY="" python main.py

# All AI endpoints work but use deterministic responses
# Useful for testing auth, endpoints, database integration
```

### Scenario 2: Development (With Gemini)

```bash
# Set API key
export GEMINI_API_KEY=your-key-here

# Start development server
python main.py

# Live AI responses from Gemini API
```

### Scenario 3: Staging (High Availability)

```bash
# Use environment secrets management
# Example with Docker secrets (if containerized)

# Start with pooled connections
DATABASE_URL="postgresql://user:pwd@pghost:5432/schoolai?sslmode=require&statement_timeout=30000"
GEMINI_API_KEY=$(cat /run/secrets/gemini_api_key)
python main.py
```

### Scenario 4: Production (Secured, Monitored)

See [Production Deployment Guide](#production-deployment-checklist) below.

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] API key from Google Cloud Console (not development key)
- [ ] Production PostgreSQL database (replicated, backed up)
- [ ] JWT secret stored in secrets manager (not in code)
- [ ] SSL/TLS certificates for HTTPS
- [ ] Monitoring and alerting configured
- [ ] All 44 tests passing: `pytest app/tests/`
- [ ] Load testing completed

### Deployment Steps

#### Step 1: Database Preparation

```bash
# Backup existing database
pg_dump schoolai_db > schoolai_db_backup.sql

# Run migrations (if any pending)
alembic upgrade head

# Verify schema has AI tables
psql -d schoolai_db -c "\dt app.*"
```

#### Step 2: Secrets Configuration

**AWS Secrets Manager** (recommended):
```bash
aws secretsmanager create-secret \
  --name schoolai/gemini_api_key \
  --secret-string "your-api-key-here"

aws secretsmanager create-secret \
  --name schoolai/jwt_secret \
  --secret-string "your-jwt-secret-here"
```

**Environment configuration** (in deployment):
```bash
export GEMINI_API_KEY=$(aws secretsmanager get-secret-value --secret-id schoolai/gemini_api_key --query SecretString --output text)
export SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id schoolai/jwt_secret --query SecretString --output text)
```

#### Step 3: Application Deployment

**Using Docker** (recommended):
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and push**:
```bash
docker build -t schoolai:latest .
docker tag schoolai:latest your-registry/schoolai:latest
docker push your-registry/schoolai:latest
```

#### Step 4: Monitoring Setup

```bash
# Monitor API errors
curl http://prod.example.com/health

# Monitor Gemini API usage (Google Cloud Console)
# Check for quota warnings and costs

# Enable application logging
LOG_LEVEL=INFO python main.py

# Forward logs to centralized logging (e.g., CloudWatch, ELK)
```

#### Step 5: Validation

```bash
# Test AI endpoint
curl -X POST http://prod.example.com/api/v1/ai/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'

# Expected: 200 with AI response or error code
# 503 Service Unavailable = Check Gemini API key

# Run smoke tests
pytest app/tests/test_health.py -v
```

---

## Production Deployment Checklist

### Infrastructure

```
┌─────────────────┐
│  Load Balancer  │ (HTTPS only)
│   (SSL/TLS)     │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    │           │          │
 ┌──▼──┐   ┌──▼──┐   ┌──▼──┐
 │App-1│   │App-2│   │App-3│ (Multiple instances)
 └──┬──┘   └──┬──┘   └──┬──┘
    │         │        │
    └────┬────┴────┬───┘
         │         │
    ┌────▼──┐  ┌──▼────┐
    │ Cache │  │  DB   │ (PostgreSQL replication)
    │(Redis)│  │Primary│
    └───────┘  └──┬────┘
                  │
              ┌───▼────┐
              │ Replica│
              └────────┘
```

### Configuration

```python
# app/core/config.py - Production settings
class ProductionSettings(Settings):
    # Database with connection pooling
    database_url: str = "postgresql://user:pwd@host:5432/db?pool_size=20&max_overflow=40"
    
    # Security
    debug: bool = False
    
    # AI
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    
    # Logging
    log_level: str = "INFO"
    
    # CORS (restrict to your domain)
    allowed_origins: list = ["https://yourdomain.com"]
```

### Monitoring Configuration

```python
# Add to main.py or middleware
from prometheus_client import Counter, Histogram
import time

# Metrics
ai_request_count = Counter('ai_requests_total', 'Total AI requests', ['method'])
ai_latency = Histogram('ai_request_seconds', 'AI request latency', ['method'])
gemini_errors = Counter('gemini_errors_total', 'Gemini API errors')

# Middleware
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    ai_latency.labels(method=request.url.path).observe(duration)
    return response
```

---

## Troubleshooting Deployment

### Issue: "Gemini API key not configured"

**Symptom**: All AI endpoints return 503, logs show fallback mode active

**Solution**:
1. Verify `GEMINI_API_KEY` environment variable is set
   ```bash
   echo $GEMINI_API_KEY  # Should not be empty
   ```
2. Check API key is valid on [Google Cloud Console](https://console.cloud.google.com/)
3. Verify API is enabled: **APIs & Services** → **generativelanguage.googleapis.com**
4. Restart application after setting environment variable

### Issue: Database Connection Timeout

**Symptom**: "FATAL: remaining connection slots are reserved"

**Solution**:
1. Increase connection pool size in `DATABASE_URL`:
   ```
   postgresql://user:pwd@host/db?pool_size=30&max_overflow=50
   ```
2. Check database active connections:
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```
3. Kill idle connections if needed:
   ```sql
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '30 min';
   ```

### Issue: Slow AI Responses

**Symptom**: Requests take > 30 seconds

**Solution**:
1. Check network latency to Gemini API
2. Monitor database query performance (RAG context retrieval)
3. Implement response caching for repeated queries
4. Check Gemini API quota and rate limits

### Issue: JWT Token Validation Fails

**Symptom**: 401 Unauthorized on protected endpoints

**Solution**:
1. Verify `SECRET_KEY` and `ALGORITHM` are consistent
2. Check token expiration: `ACCESS_TOKEN_EXPIRE_MINUTES`
3. Ensure token is in `Authorization: Bearer {token}` format
4. Verify user claims include `sub` (user_id) and `school_id`

---

## Running Tests

### Local Development

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests (44 total)
pytest -v app/tests/

# Run AI tests only (26 tests)
pytest -v app/tests/test_ai.py

# With coverage report
pytest --cov=app app/tests/ --cov-report=html
```

### CI/CD Pipeline Example (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: schoolai_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.13
      
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-asyncio
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/schoolai_test
          SECRET_KEY: test-secret-key
        run: pytest -v app/tests/
```

---

## Maintenance

### Regular Tasks

**Weekly**:
- Monitor error logs
- Check Gemini API quota usage
- Verify database backups

**Monthly**:
- Review performance metrics
- Update dependencies: `pip list --outdated`
- Run full test suite

**Quarterly**:
- Security audit
- Load testing
- Database maintenance (VACUUM, ANALYZE)

### Updating Dependencies

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade google-generativeai

# Update all (use with caution)
pip install --upgrade -r requirements.txt

# Run tests after update
pytest app/tests/
```

### Backup and Recovery

```bash
# Backup database
pg_dump schoolai_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql schoolai_db < backup_20240115_100000.sql

# Backup API key (store securely)
# Use secrets manager, not files
```

---

## Performance Tuning

### Database Query Optimization

```sql
-- Create indexes for RAG queries
CREATE INDEX idx_campaign_school_id ON campaigns(school_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_competitor_school_id ON competitors(school_id) WHERE deleted_at IS NULL;

-- Check query plans
EXPLAIN ANALYZE SELECT * FROM campaigns WHERE school_id = ? AND deleted_at IS NULL;
```

### Connection Pooling

```python
# Recommended for production
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Number of connections to keep open
    max_overflow=40,        # Additional connections when pool full
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Test connections before use
    echo=False              # Disable SQL logging in production
)
```

### Caching RAG Context

```python
# Optional: Cache frequently accessed contexts
from functools import lru_cache
from datetime import datetime, timedelta

class CachedRAGService(RAGService):
    def __init__(self, db, school_id, cache_ttl_minutes=5):
        super().__init__(db, school_id)
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.cache = {}
        self.cache_time = {}
    
    def get_school_context(self):
        if self._cache_valid('school'):
            return self.cache['school']
        
        context = super().get_school_context()
        self.cache['school'] = context
        self.cache_time['school'] = datetime.now()
        return context
    
    def _cache_valid(self, key):
        if key not in self.cache:
            return False
        return datetime.now() - self.cache_time[key] < self.cache_ttl
```

---

## Security Best Practices

1. **Never commit secrets** - Use environment variables or secrets manager
2. **API Key rotation** - Rotate Gemini keys quarterly
3. **Rate limiting** - Limit AI API calls per user/school
4. **Input validation** - All inputs validated by Pydantic
5. **Audit logging** - Log all AI analyses for compliance
6. **HTTPS only** - Force HTTPS in production
7. **CORS configuration** - Restrict to known domains
8. **JWT expiration** - Short-lived tokens (30 min recommended)

---

## Getting Help

### Common Questions

**Q: Can I use AI module without Gemini API key?**
A: Yes, fallback mode activates automatically. Responses are deterministic but functional.

**Q: What's the Gemini API cost?**
A: Free tier: 60 requests/minute, 1.5M tokens/day. See [pricing](https://ai.google.dev/pricing).

**Q: How long do AI requests take?**
A: Typically 1-5 seconds with Gemini, < 100ms with fallback.

**Q: Is tenant data secure?**
A: Yes, all queries filter by school_id. Verified in 26 unit tests.

### Support Resources

- [Google Generative AI Python SDK](https://ai.google.dev/tutorials/python_quickstart)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/20/orm/)
- [Project README](../README.md)

