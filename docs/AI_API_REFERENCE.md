# AI API Quick Reference

## Base URL
```
http://localhost:8000/api/v1
https://api.example.com/api/v1  # Production
```

## Authentication
All AI endpoints require JWT bearer token:
```
Authorization: Bearer {jwt_token}
```

---

## Endpoints

### 1. POST /ai/chat
**Chat with AI assistant grounded in school data**

**Request**:
```json
{
  "message": "What campaigns should I focus on?",
  "include_full_context": true
}
```

**Response** (200 OK):
```json
{
  "response": "Based on your data, I recommend focusing on your Email Q4 campaign which has achieved 4.2x ROI. This outperforms your average by 2x.",
  "context_used": {
    "school_id": "550e8400-e29b-41d4-a716-446655440000",
    "campaigns_count": 5,
    "competitors_count": 3,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "model": "gemini-pro"
}
```

**Error** (400):
```json
{
  "detail": "User not linked to school"
}
```

**Error** (503):
```json
{
  "detail": "AI service temporarily unavailable. Using fallback mode. Error: API quota exceeded"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What campaigns should I focus on?",
    "include_full_context": true
  }'
```

---

### 2. POST /ai/swot
**SWOT Analysis of current marketing position**

**Request**:
```json
{
  "focus_area": "marketing"
}
```

**Valid focus_area values**: `marketing`, `campaigns`, `competitive`, `general` (default)

**Response** (200 OK):
```json
{
  "strengths": [
    "Email channel demonstrates 4.2x ROI with 12.5% engagement rate",
    "Strong seasonal Q4 performance (+35% vs baseline)",
    "Diverse campaign portfolio across 5 channels"
  ],
  "weaknesses": [
    "Social media campaigns underperforming (0.8x ROI)",
    "Limited budget allocation to high-performing channels",
    "Low repeat engagement on paid search"
  ],
  "opportunities": [
    "Scale email campaigns by 20-30% based on ROI potential",
    "Develop AI-powered personalization for email sequences",
    "Test influencer partnerships in social channel"
  ],
  "threats": [
    "Competitor A showing 5.2x email engagement rate",
    "Market saturation in core demographic",
    "Budget constraints limiting experimentation"
  ]
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/swot \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "focus_area": "marketing"
  }'
```

---

### 3. POST /ai/recommendations
**Marketing recommendations based on campaign analysis**

**Request**:
```json
{}
```

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "priority": "HIGH",
      "area": "Budget Allocation",
      "recommendation": "Shift 20% of budget from underperforming social campaigns to proven email channel",
      "expected_impact": "12-15% ROI improvement",
      "effort": "LOW",
      "timeline_days": 7
    },
    {
      "priority": "HIGH",
      "area": "Campaign Optimization",
      "recommendation": "Implement A/B testing on email subject lines - current variations show 8% engagement variance",
      "expected_impact": "3-5% engagement lift",
      "effort": "MEDIUM",
      "timeline_days": 14
    },
    {
      "priority": "MEDIUM",
      "area": "New Channel Testing",
      "recommendation": "Pilot SMS marketing channel with subset of high-value contacts",
      "expected_impact": "Potential 2.5x ROI if performance matches industry benchmarks",
      "effort": "HIGH",
      "timeline_days": 30
    }
  ],
  "summary": "Focus on maximizing ROI of existing channels before expanding portfolio. Key lever: shift budget to email and implement testing program.",
  "estimated_roi_improvement": "12-15%",
  "confidence_level": "HIGH"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 4. POST /ai/competitor-insights
**Competitive analysis and threat assessment**

**Request**:
```json
{}
```

**Response** (200 OK):
```json
{
  "competitive_landscape": "Moderate competition - 1 high-threat competitor, 1 medium, 1 low threat",
  "threat_analysis": [
    {
      "competitor_id": "comp-001",
      "competitor_name": "Competitor A",
      "threat_level": "HIGH",
      "threat_score": 8.5,
      "reason": "Superior email engagement (12.5% vs your 10.2%)",
      "market_share_estimate": "35%",
      "key_differentiator": "Advanced personalization and segmentation",
      "recommendation": "Develop proprietary personalization model"
    },
    {
      "competitor_id": "comp-002",
      "competitor_name": "Competitor B",
      "threat_level": "MEDIUM",
      "threat_score": 5.2,
      "reason": "Strong in social media, weak in email",
      "market_share_estimate": "20%",
      "key_differentiator": "Social media dominance",
      "recommendation": "Defend email position while monitoring social growth"
    }
  ],
  "market_position": "You lead in email ROI (4.2x vs competitor average 2.8x) but lag in overall campaign diversity",
  "recommendations": [
    "Maintain and expand email channel advantage",
    "Develop social media capabilities to compete",
    "Monitor Competitor A's new initiatives"
  ]
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/competitor-insights \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 5. POST /ai/campaign-optimization
**Optimization suggestions for underperforming campaigns**

**Request**:
```json
{}
```

**Response** (200 OK):
```json
{
  "low_roi_campaigns": [
    {
      "campaign_id": "camp-001",
      "campaign_name": "Social Q4 2024",
      "current_roi": 0.8,
      "budget": 5000,
      "spend": 4200,
      "engagement_rate": 2.1,
      "optimization_suggestions": [
        "Reduce audience targeting breadth - too many impressions, low conversion",
        "Shift to lookalike audiences based on high-engagement segments",
        "Implement frequency capping - current avg 8 impressions per user",
        "Test video creative - current static creative underperforms"
      ],
      "estimated_improvement": "1.5-2.0x ROI improvement",
      "recommended_action": "PAUSE_AND_REOPTIMIZE"
    }
  ],
  "priority_optimizations": [
    {
      "rank": 1,
      "action": "Reallocate budget to email channel",
      "current_allocation": "$5000 (20%)",
      "suggested_allocation": "$3000 (12%)",
      "reason": "ROI 0.8x vs email 4.2x",
      "expected_impact": "8-10% total ROI improvement",
      "effort": "LOW",
      "timeline": "Immediate"
    },
    {
      "rank": 2,
      "action": "Implement A/B test on email subject lines",
      "estimated_uplift": "3-5% engagement",
      "effort": "LOW",
      "timeline": "1 week"
    }
  ],
  "summary": "3 campaigns below target ROI. Primary lever: shift budget to email. Secondary: A/B testing.",
  "total_potential_savings": "$2000",
  "total_potential_roi_improvement": "8-10%"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/campaign-optimization \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 6. POST /ai/predictions
**Trend predictions based on historical campaign data**

**Request**:
```json
{
  "time_horizon_days": 90
}
```

**Response** (200 OK):
```json
{
  "predictions": [
    {
      "metric": "Email Engagement Rate",
      "current_value": "10.2%",
      "trend": "INCREASING",
      "confidence": "HIGH",
      "forecast": "Expected to reach 11.5-12.0% over 90 days",
      "forecast_basis": "Consistent +0.15% monthly growth trend",
      "recommendation": "Capitalize on momentum - increase email budget",
      "risk_factors": ["Market saturation", "Email fatigue"]
    },
    {
      "metric": "Campaign ROI (Overall)",
      "current_value": "3.2x",
      "trend": "STABLE",
      "confidence": "MEDIUM",
      "forecast": "Expected to remain in 3.0-3.4x range",
      "forecast_basis": "High variance between channels; email stable, social improving",
      "recommendation": "Stabilization achieved - now optimize for growth",
      "risk_factors": ["Competitive pressure", "Budget constraints"]
    },
    {
      "metric": "Social Media ROI",
      "current_value": "0.8x",
      "trend": "INCREASING",
      "confidence": "MEDIUM",
      "forecast": "Expected to reach 1.2-1.5x by quarter end",
      "forecast_basis": "Recent creative changes showing +0.1x monthly improvement",
      "recommendation": "Continue testing approach - potential channel expansion",
      "risk_factors": ["Algorithm changes", "Ad cost increases"]
    }
  ],
  "seasonal_factors": {
    "Q1_2024": "Typically 15-20% lower engagement (budget constraints)",
    "Q4_2024": "30-35% higher engagement (year-end budgets)",
    "Spring": "Strong social media performance"
  },
  "recommendation": "Prepare for Q1 seasonal dip - pre-test campaigns and optimize messaging for lower engagement environment",
  "confidence_level": "MEDIUM"
}
```

**cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/predictions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_horizon_days": 90
  }'
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "User not linked to school"
}
```
**Cause**: User doesn't have a `school_id` in their profile  
**Fix**: Link user to school via admin API

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
**Cause**: Missing or invalid JWT token  
**Fix**: Include valid `Authorization: Bearer {token}` header

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```
**Cause**: User role insufficient for this endpoint  
**Fix**: Contact admin to upgrade permissions

### 503 Service Unavailable
```json
{
  "detail": "AI service temporarily unavailable. Using fallback mode. Error: API quota exceeded"
}
```
**Cause**: Gemini API error (quota, rate limit, network issue)  
**Fix**: Fallback mode active. Check Google Cloud Console quota.

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
**Cause**: Unexpected error in AI service  
**Fix**: Check application logs, contact support

---

## Response Codes Summary

| Code | Meaning | When to Retry |
|------|---------|---------------|
| 200 | Success - Response complete | No |
| 400 | Bad request - Check input | No (fix input) |
| 401 | Unauthorized - Invalid token | Yes (refresh token) |
| 403 | Forbidden - Insufficient permissions | No (contact admin) |
| 503 | Service unavailable | Yes (exponential backoff) |
| 500 | Server error | Yes (exponential backoff) |

---

## Request/Response Examples

### Example 1: Chat with Full Context

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How can I improve my email campaign performance?",
    "include_full_context": true
  }'
```

**Response**:
```json
{
  "response": "Based on your campaign data, your email channel is your strongest performer with 4.2x ROI. To improve further: (1) Segment your audience more granularly - you're currently using only 2 segments but competitors use 5-7, (2) Implement dynamic content blocks based on user behavior, (3) Test new send times - your data shows 8% higher opens at 9am vs 2pm. Your current email list health is good (98.5% validity rate), so focus on content optimization.",
  "context_used": {
    "school_id": "550e8400-e29b-41d4-a716-446655440000",
    "campaigns_count": 5,
    "competitors_count": 3,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "model": "gemini-pro"
}
```

### Example 2: SWOT Analysis (Fallback Mode)

**Request** (Gemini API unavailable):
```bash
curl -X POST http://localhost:8000/api/v1/ai/swot \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{"focus_area": "marketing"}'
```

**Response** (Fallback):
```json
{
  "strengths": [
    "Strong performance: 2 campaigns with ROI > 2.0x",
    "Active market presence"
  ],
  "weaknesses": [
    "Underperforming areas: 1 campaign with ROI < 1.0x",
    "Limited campaign diversity"
  ],
  "opportunities": [
    "Scale high-ROI campaigns",
    "Explore new marketing channels"
  ],
  "threats": [
    "Competitive pressure in core markets",
    "Market saturation"
  ]
}
```

### Example 3: Predictions with Custom Horizon

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/predictions \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "time_horizon_days": 180
  }'
```

---

## Rate Limiting

**Current Limits** (recommended in production):
- 10 requests per minute per user
- 1000 requests per hour per school
- Burst: 3 requests within 1 second

**Response Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1705329000
```

**Rate Limit Error** (429):
```json
{
  "detail": "Too many requests. Please retry after 60 seconds."
}
```

---

## Performance Tips

1. **Cache responses** - AI responses don't change frequently, cache for 5-10 minutes
2. **Use include_full_context=false** - For simple chats, reduce latency
3. **Batch requests** - Don't call multiple endpoints simultaneously
4. **Fallback gracefully** - Handle 503 errors with fallback UI

---

## Testing in Browser/Postman

**Import Collection URL**:
```
https://api.example.com/api/v1/openapi.json
```

**Or manually add headers in Postman**:
1. Create new request
2. URL: `http://localhost:8000/api/v1/ai/chat`
3. Method: `POST`
4. Header: `Authorization: Bearer {your_token}`
5. Body: `{"message": "test"}`
6. Send

---

## Webhook Notifications (Future)

*Currently not implemented. Can be added to notify school when:*
- New AI insights available
- Prediction confidence changes
- Campaign optimization recommended

---

## Rate Limits & Quotas

**Free Tier** (Gemini API):
- 60 requests/minute
- 1.5M tokens/day
- Shared across all users

**Paid Plans** (see Google Cloud Console):
- Variable based on usage tier
- Recommended: $0.00375 per 1000 tokens

**School Quotas** (application level):
- Configurable per subscription tier
- STARTER: 100 AI requests/month
- PROFESSIONAL: 1000 requests/month
- ENTERPRISE: Unlimited

---

## Troubleshooting API Calls

**403 Forbidden - Insufficient Permissions**
```bash
# Check your user's role
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer {token}"

# Verify school_id is present
```

**503 Service Unavailable**
```bash
# Check Gemini API key is configured
curl http://localhost:8000/health

# If "gemini_configured": false, set GEMINI_API_KEY
```

**Empty Response**
```bash
# Verify school has data (campaigns, competitors)
curl http://localhost:8000/api/v1/schools/me \
  -H "Authorization: Bearer {token}"

# Add test data if needed
```

---

## OpenAPI/Swagger Documentation

**Available at**:
- Development: `http://localhost:8000/docs` (Swagger UI)
- Production: `https://api.example.com/docs`
- OpenAPI JSON: `/api/v1/openapi.json`

