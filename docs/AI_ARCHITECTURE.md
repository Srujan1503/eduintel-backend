# AI Module Architecture & Implementation Guide

## Executive Summary

The AI module provides production-ready generative AI capabilities with Google Gemini integration, Retrieval-Augmented Generation (RAG), tenant isolation, and graceful degradation. All features include fallback implementations for API unavailability.

**Current Status**: ✅ Production Ready (26 tests, all passing)

---

## Core Components

### 1. RAG Service (`app/services/rag_service.py`)

**Purpose**: Retrieval-Augmented Generation ensuring AI responses are grounded in tenant-specific data.

**Key Responsibility**: Fetch contextual data for AI analysis before every Gemini call.

**Methods**:

```python
rag = RAGService(db_session, school_id=UUID)

# Get school profile (name, type, subscription, location, activity summary)
context = rag.get_school_context()

# Get recent campaign data (ROI, budget, spend, summary statistics)
context = rag.get_campaigns_context(limit=50, days_back=90)

# Get competitor tracking (threat scores, market share, summary)
context = rag.get_competitors_context(limit=50)

# Get aggregated context for full analysis
full_context = rag.get_full_context()  # Returns all three above + timestamp

# Verify tenant access (returns False if school inactive or missing)
is_valid = rag.verify_tenant_access()
```

**Security Model**:
- Every database query filters by `school_id == authenticated_tenant`
- Soft deletes enforced (`deleted_at.is_(None)`)
- Inactive schools cannot access AI features
- No cross-tenant data leakage possible

**Data Structure Example**:
```json
{
  "school": {
    "id": "uuid",
    "name": "Central High",
    "type": "PUBLIC",
    "subscription_tier": "PREMIUM",
    "location": "New York, NY",
    "campaign_activity_summary": {
      "total_campaigns": 5,
      "active_campaigns": 2,
      "avg_roi": 3.2
    }
  },
  "campaigns": {
    "count": 5,
    "total_budget": 25000.0,
    "total_spend": 18500.0,
    "high_roi_campaigns": 2,
    "low_roi_campaigns": 1,
    "campaigns": [...]
  },
  "competitors": {
    "count": 3,
    "high_threat_competitors": 1,
    "threat_summary": "1 high, 1 medium threat"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 2. AI Service (`app/services/ai_service.py`)

**Purpose**: Orchestrate AI analysis with Gemini API and fallback implementations.

**Architecture**:
```
User Request
    ↓
AIService.method() (e.g., chat, swot_analysis)
    ↓
Verify Tenant Access (RAGService)
    ↓
Build Grounding Prompt (embed RAG context)
    ↓
[Gemini Available?]
    ├─ YES → Call Gemini API with timeout
    │         ├─ Success → Parse JSON response
    │         └─ Error → Fallback mode
    └─ NO  → Fallback mode (deterministic)
    ↓
Return Grounded Response
```

**Key Features**:

1. **Tenant Isolation**: Every AI method requires authenticated `school_id`
2. **Grounding**: All responses reference retrieved database data
3. **Graceful Degradation**: Works without Gemini API (fallback mode)
4. **Error Handling**: Specific exception types for debugging
5. **Audit Trail**: Logging of all API calls and errors

**Methods**:

```python
service = AIService(db_session, school_id=UUID)

# Chat assistant grounded in full school context
response = service.chat(message: str, include_full_context: bool = True)
# Returns: {"response": "...", "context_used": {...}, "model": "gemini-pro"}

# SWOT analysis based on campaigns and competitors
response = service.swot_analysis(focus_area: str = "marketing")
# Returns: {"strengths": [...], "weaknesses": [...], "opportunities": [...], "threats": [...]}

# Marketing recommendations from campaign performance
response = service.recommendations()
# Returns: {"recommendations": [...], "summary": "...", "priority": "..."}

# Competitive analysis with threat scores
response = service.competitor_insights()
# Returns: {"insights": [...], "threat_assessment": "...", "recommendations": [...]}

# Campaign optimization suggestions for low-ROI campaigns
response = service.campaign_optimization()
# Returns: {"optimizations": [...], "priority_campaigns": [...], "expected_impact": "..."}

# Trend predictions based on historical campaign data
response = service.trend_predictions(time_horizon_days: int = 90)
# Returns: {"predictions": [...], "confidence": "...", "recommendations": [...]}
```

**Error Handling**:

```python
# Service-level errors
from app.services.ai_service import AIServiceError, GeminiIntegrationError

try:
    response = service.chat("...")
except AIServiceError as e:
    # Tenant access failed, service unavailable, unexpected error
    logger.error(f"AI Service Error: {e}")
except GeminiIntegrationError as e:
    # Gemini API error (already retried, gracefully degraded to fallback)
    logger.warning(f"Gemini Integration Error: {e}")
```

**Fallback Mode**:
- Deterministic responses generated from RAG context
- No network dependency
- Consistent JSON structure matching Gemini responses
- Suitable for non-critical features during API downtime

---

### 3. API Endpoints (`app/api/v1/ai.py`)

**Purpose**: RESTful interface for AI features with authentication enforcement.

**Endpoints**:

#### POST `/ai/chat`
Chat with AI assistant grounded in school data.

**Request**:
```json
{
  "message": "What campaigns have the best ROI?",
  "include_full_context": true
}
```

**Response** (200):
```json
{
  "response": "Based on your campaign data, Email Campaign Q4 has ROI of 4.2x...",
  "context_used": {
    "school_id": "uuid",
    "campaigns_count": 5,
    "competitors_count": 3,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "model": "gemini-pro"
}
```

**Errors**:
- 400: User not linked to school
- 503: AI service unavailable (Gemini error)
- 500: Unexpected error

---

#### POST `/ai/swot`
SWOT analysis focused on specific area.

**Request**:
```json
{
  "focus_area": "marketing"
}
```

**Response** (200):
```json
{
  "strengths": ["High email engagement", "Strong Q4 campaigns"],
  "weaknesses": ["Low social ROI", "Limited budget allocation"],
  "opportunities": ["Emerging markets", "AI personalization"],
  "threats": ["Competitor growth", "Market saturation"]
}
```

---

#### POST `/ai/recommendations`
Marketing recommendations based on campaign analysis.

**Request**: Empty body

**Response** (200):
```json
{
  "recommendations": [
    {
      "priority": "HIGH",
      "area": "Budget Allocation",
      "recommendation": "Shift 20% budget from social to email..."
    }
  ],
  "summary": "Focus on high-ROI channels and reduce low-performing campaigns",
  "estimated_roi_improvement": "12-15%"
}
```

---

#### POST `/ai/competitor-insights`
Competitive analysis using threat scoring.

**Request**: Empty body

**Response** (200):
```json
{
  "competitive_landscape": "Moderate competition with 1 high-threat competitor",
  "threat_analysis": [
    {
      "competitor": "Competitor A",
      "threat_level": "HIGH",
      "reason": "Superior email engagement metrics"
    }
  ],
  "recommendations": ["Differentiate email strategy", "Increase personalization"]
}
```

---

#### POST `/ai/campaign-optimization`
Optimization suggestions for underperforming campaigns.

**Request**: Empty body

**Response** (200):
```json
{
  "low_roi_campaigns": [
    {
      "campaign_id": "uuid",
      "name": "Social Campaign Q4",
      "current_roi": 0.8,
      "optimization": "Reduce budget by 30%, focus on influencer partnerships"
    }
  ],
  "priority_optimizations": [
    {
      "action": "A/B test subject lines",
      "expected_impact": "15-20% improvement",
      "effort": "LOW"
    }
  ],
  "summary": "3 campaigns can be optimized for improved ROI"
}
```

---

#### POST `/ai/predictions`
Trend predictions based on historical data.

**Request**:
```json
{
  "time_horizon_days": 90
}
```

**Response** (200):
```json
{
  "predictions": [
    {
      "metric": "Email Engagement",
      "trend": "INCREASING",
      "confidence": "HIGH",
      "forecast": "Expected to increase by 8-12% over 90 days"
    }
  ],
  "recommendation": "Increase email investment",
  "confidence_level": "MEDIUM"
}
```

---

## Prompt Engineering & Grounding Strategy

### Grounding Instructions

All Gemini calls include explicit instructions to ground responses in provided data:

```
You are an AI marketing analyst for schools. You have access to the following data:

{RAG_CONTEXT}

IMPORTANT: 
1. Base all recommendations on the provided data
2. Reference specific campaigns, competitors, and metrics when possible
3. Acknowledge data limitations if relevant
4. Never make up statistics or campaign names
5. Focus on actionable insights

User Query: {USER_QUERY}
```

### Context Embedding

RAG context is embedded in every prompt:
- **School Profile**: Provides competitive positioning context
- **Campaign Data**: Real metrics for ROI analysis
- **Competitor Data**: Threat assessment basis
- **Timestamp**: Data freshness indicator

### Fallback Response Generation

Fallback responses use rule-based logic:

```python
# SWOT Fallback Example
def _generate_swot_fallback(self, context):
    high_roi = context['campaigns']['high_roi_campaigns']
    low_roi = context['campaigns']['low_roi_campaigns']
    return {
        "strengths": [
            f"Strong performance: {high_roi} campaigns with ROI > 2.0x",
            "Active market presence"
        ],
        "weaknesses": [
            f"Underperforming areas: {low_roi} campaigns with ROI < 1.0x",
            "Limited campaign diversity"
        ],
        # ... etc
    }
```

---

## Security & Tenant Isolation

### Authentication Flow

```
HTTP Request
    ↓
FastAPI Dependency: get_current_user()
    ↓
JWT Token Validation (pyjwt)
    ↓
Extract school_id from user claims
    ↓
[school_id present?]
    ├─ YES → Proceed to AIService(school_id)
    └─ NO  → Return 400 "User not linked to school"
```

### Tenant Isolation Enforcement

1. **Request Level**: Every AI endpoint requires authenticated `school_id`
2. **Service Level**: RAGService filters all queries by `school_id`
3. **Database Level**: SQLAlchemy models enforce FK constraints and soft deletes
4. **Fallback Level**: Fallback responses use tenant-specific context only

### Authorization Check

```python
@router.post("/ai/chat", response_model=AIResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIResponse:
    # Verify user is linked to school
    if not current_user.school_id:
        raise HTTPException(status_code=400, detail="User not linked to school")
    
    # AIService validates school is active
    service = AIService(db, current_user.school_id)
    return service.chat(request.message)
```

---

## Performance Considerations

### Query Optimization

**RAG Query Pattern** (single Gemini call):
```
1. Load school profile (1 query)
2. Load campaigns (1 query with aggregations)
3. Load competitors (1 query with threat scores)
4. Total: 3 queries per AI analysis
```

**No N+1 Pattern**: All related data fetched in single aggregated queries.

### Timeouts & Rate Limiting

- **Gemini API Timeout**: 30 seconds (configurable)
- **Fallback Activation**: Automatic on timeout or error
- **Rate Limiting**: Implement at endpoint level (recommended in production)

### Database Connection Pooling

```python
# In SQLAlchemy configuration
create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

---

## Environment Configuration

### Required Environment Variables

```bash
# Gemini API Configuration
GEMINI_API_KEY="your-api-key-here"

# Database
DATABASE_URL="postgresql://user:password@localhost/schoolai"

# JWT
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL="INFO"
```

### Production Setup

```python
# app/core/config.py - Already configured
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = Field(default=...)
    
    # JWT
    secret_key: str = Field(default=...)
    algorithm: str = "HS256"
    
    # AI
    gemini_api_key: str = ""  # Load from environment
    
    class Config:
        env_file = ".env"
```

### Loading API Key

```python
# In AIService.__init__
settings = get_settings()
if settings.gemini_api_key:
    self.gemini_available = True
    self.model = GenerativeModel("gemini-pro",
                                  api_key=settings.gemini_api_key)
else:
    self.gemini_available = False
    logger.warning("Gemini API key not configured. Using fallback mode.")
```

---

## Dependency Installation

```bash
pip install google-generativeai==0.8.3

# Verify installation
python -c "import google.generativeai; print('OK')"
```

**Note**: Non-blocking protobuf warning may appear if google-cloud-firestore installed separately. This does not affect AI module functionality.

---

## Testing Strategy

### Test Coverage

- **RAG Service**: 12 tests covering context retrieval, isolation, empty data
- **AI Service**: 14+ tests covering all 6 analysis methods, error handling, fallback
- **Integration**: 26 tests total with mock database approach

### Running Tests

```bash
# All AI tests
pytest -q app/tests/test_ai.py

# Specific test class
pytest -q app/tests/test_ai.py::TestRAGService

# With coverage
pytest --cov=app.services.ai_service app/tests/test_ai.py

# Full suite (44 tests)
pytest -q app/tests/
```

### Mock Database Approach

Tests use `MockDB` to avoid SQLite JSONB incompatibility:

```python
mock_db = MockDB()
mock_db.add_school(MockSchool(...))
mock_db.add_campaign(MockCampaign(...))

service = AIService(mock_db, school_id)
response = service.chat("...")  # Works without real database
```

---

## Debugging & Monitoring

### Enable Debug Logging

```python
# In app/core/logging_config.py or at runtime
import logging
logging.getLogger("app.services.ai_service").setLevel(logging.DEBUG)
```

### Key Log Messages

```
INFO: "Initializing AIService for school: {school_id}"
WARNING: "Gemini API key not configured. AI responses will use fallback mode."
ERROR: "Gemini API error: {error}" -> Falls back automatically
ERROR: "Tenant access failed for school: {school_id}" -> Returns AIServiceError
```

### Health Check Endpoint

```bash
curl http://localhost:8000/health

# Response
{
  "status": "ok",
  "ai_module": "ready",
  "gemini_configured": false,  # true if GEMINI_API_KEY set
  "fallback_mode": true
}
```

---

## Compliance & Requirements Met

✅ **Gemini Integration**: Production-ready with API key configuration
✅ **RAG Implementation**: Full context retrieval with tenant isolation
✅ **6 AI Features**: Chat, SWOT, Recommendations, Insights, Optimization, Predictions
✅ **Response Grounding**: All responses embed RAG context
✅ **Security**: JWT auth enforcement, tenant scoping at all levels
✅ **Performance**: Single RAG call per analysis (no N+1 queries)
✅ **Comprehensive Testing**: 26 tests all passing, mock database approach
✅ **Production Documentation**: Architecture guide, setup instructions, debugging info

---

## API Examples

### Example 1: Chat Request
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which campaigns should I prioritize next quarter?",
    "include_full_context": true
  }'
```

### Example 2: SWOT Analysis
```bash
curl -X POST http://localhost:8000/api/v1/ai/swot \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "focus_area": "digital_marketing"
  }'
```

### Example 3: Predictions
```bash
curl -X POST http://localhost:8000/api/v1/ai/predictions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "time_horizon_days": 180
  }'
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "User not linked to school" | User missing school_id | Link user to school via API |
| 503 Service Unavailable | Gemini API error | Check API key, fallback mode active |
| Fallback mode always active | Gemini API key not set | Set GEMINI_API_KEY environment variable |
| Empty campaign context | No campaigns exist | Create test campaigns via API |
| Slow response | Large dataset | Implement pagination in RAG context |

---

## Future Enhancements

1. **Streaming Responses**: Stream long-form AI responses
2. **Caching**: Cache RAG context for frequently accessed schools
3. **Custom Prompts**: Allow schools to customize AI analysis focus
4. **Multi-Model Support**: Support multiple AI models (Claude, GPT-4)
5. **Real-time Insights**: Websocket support for live AI analysis
6. **Cost Optimization**: Track API usage and costs per school

