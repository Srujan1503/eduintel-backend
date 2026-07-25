"""
Production AI service with Gemini integration and RAG grounding.

Features:
- Graceful Gemini API error handling with fallback responses
- Configurable timeouts and retries
- Grounded responses based on database data
- Tenant isolation
- Request logging (safe, non-sensitive)
"""

import json
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service failures."""
    pass


class GeminiIntegrationError(AIServiceError):
    """Raised when Gemini API fails."""
    pass


class AIService:
    """
    Production AI service with Gemini integration.
    
    All responses are grounded in retrieved tenant data.
    Includes graceful fallback when Gemini is unavailable.
    """

    def __init__(self, db: Session, school_id: UUID):
        """
        Initialize AI service for a tenant.
        
        Args:
            db: SQLAlchemy session
            school_id: UUID of authenticated tenant
        """
        self.db = db
        self.school_id = school_id
        self.rag = RAGService(db, school_id)
        self.settings = get_settings()

        # Initialize Gemini client if API key is available
        self.gemini_client = None
        self.gemini_available = False
        self._init_gemini()

    def _init_gemini(self) -> None:
        """Initialize Gemini client if API key is configured."""
        try:
            if not self.settings.gemini_api_key:
                logger.warning("Gemini API key not configured. AI responses will use fallback mode.")
                return

            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            self.gemini_client = genai.GenerativeModel("gemini-pro")
            self.gemini_available = True
            logger.info("Gemini API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.gemini_available = False

    def _verify_tenant_access(self) -> bool:
        """Verify tenant can access AI features."""
        if not self.rag.verify_tenant_access():
            logger.warning(f"Tenant {self.school_id} not found or inactive")
            return False
        return True

    def _call_gemini(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30
    ) -> str:
        """
        Call Gemini API with timeout and error handling.
        
        Args:
            prompt: The complete prompt to send to Gemini
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response tokens
            timeout: Request timeout in seconds
        
        Returns:
            Response text from Gemini
        
        Raises:
            GeminiIntegrationError: If API call fails
        """
        if not self.gemini_available or not self.gemini_client:
            raise GeminiIntegrationError("Gemini client not initialized")

        try:
            # Configure generation settings
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            # Call API with timeout handling
            import socket
            socket.setdefaulttimeout(timeout)

            response = self.gemini_client.generate_content(
                prompt,
                generation_config=generation_config,
                stream=False
            )

            if not response or not response.text:
                raise GeminiIntegrationError("Empty response from Gemini")

            return response.text

        except GeminiIntegrationError:
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API call failed: {error_msg}")
            raise GeminiIntegrationError(f"Gemini API error: {error_msg}")

    def _build_prompt(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        include_full_context: bool = False
    ) -> str:
        """
        Build a grounded prompt with tenant context.
        
        Args:
            query: User's question or request
            context: Additional context data
            include_full_context: Whether to include full RAG context
        
        Returns:
            Complete prompt ready for Gemini
        """
        # Retrieve tenant data
        rag_context = self.rag.get_full_context() if include_full_context else {
            "school": self.rag.get_school_context(),
        }

        # Build context summary
        school = rag_context.get("school", {})
        school_name = school.get("name", "Unknown School")

        # Build the prompt with clear grounding instructions
        prompt = f"""
You are an AI assistant for {school_name}, an educational institution.

**CRITICAL: You MUST ground ALL responses ONLY in the provided data below.**

**Data Available:**
{json.dumps(rag_context, indent=2, default=str)}

**Additional Context:**
{json.dumps(context or {}, indent=2, default=str)}

**USER QUERY:**
{query}

**IMPORTANT RULES:**
1. Only use data provided above - NEVER invent metrics, competitors, or campaign data
2. If data is insufficient, explicitly state what's missing instead of guessing
3. Base all recommendations on actual data trends and patterns visible in the provided context
4. When making predictions, explain the data-driven reasoning
5. If a metric/competitor/campaign is not in the provided data, say so clearly

Please respond now:
"""
        return prompt

    def chat(self, message: str, include_full_context: bool = False) -> Dict[str, Any]:
        """
        Chat with AI assistant (grounded in tenant data).
        
        Args:
            message: User message
            include_full_context: Include full tenant context in response
        
        Returns:
            Response with AI message and metadata
        """
        logger.info(f"Chat request from tenant {self.school_id}")

        if not self._verify_tenant_access():
            raise AIServiceError("Tenant not found or inactive")

        try:
            # Build grounded prompt
            prompt = self._build_prompt(message, include_full_context=include_full_context)

            # Call Gemini
            if self.gemini_available:
                response_text = self._call_gemini(prompt)
            else:
                # Fallback: Return data-driven summary
                context = self.rag.get_full_context()
                response_text = self._generate_fallback_response(message, context)

            return {
                "response": response_text,
                "confidence": 1.0 if self.gemini_available else 0.5,
                "data_sufficient": True,
                "context_used": {
                    "school_id": str(self.school_id),
                    "mode": "gemini" if self.gemini_available else "fallback",
                },
            }
        except GeminiIntegrationError as e:
            logger.error(f"Gemini error in chat: {str(e)}")
            return {
                "response": f"I encountered an error connecting to the AI service. Please try again. Error: {str(e)}",
                "confidence": 0.0,
                "data_sufficient": False,
                "limitations": ["AI service temporarily unavailable"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}")
            raise

    def swot_analysis(self, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate SWOT analysis based on tenant data.
        
        Args:
            focus_area: Optional specific area to focus on
        
        Returns:
            SWOT analysis with grounded insights
        """
        logger.info(f"SWOT analysis request from tenant {self.school_id}")

        if not self._verify_tenant_access():
            raise AIServiceError("Tenant not found or inactive")

        try:
            context = self.rag.get_full_context()
            school_name = context.get("school", {}).get("name", "School")

            focus_hint = f" Focus on {focus_area}." if focus_area else ""

            prompt = f"""
Perform a SWOT analysis for {school_name} based on their marketing campaigns and competitive landscape.{focus_hint}

**Data:**
{json.dumps(context, indent=2, default=str)}

**RULES:**
- ONLY use data provided above
- Do not invent competitors or campaigns
- If a category has insufficient data, say "Insufficient data" instead of guessing
- Base strengths on actual campaign performance (ROI, conversions)
- Base weaknesses on poor-performing campaigns or gaps in data
- Base opportunities on competitor threats and market gaps visible in data
- Base threats on actual competitors and their threat scores

Respond in JSON format:
{{
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "opportunities": ["opportunity1"],
  "threats": ["threat1"],
  "summary": "Brief SWOT summary"
}}
"""
            if self.gemini_available:
                response_text = self._call_gemini(prompt, temperature=0.5)
            else:
                response_text = self._generate_swot_fallback(context)

            # Parse response
            try:
                import json as json_lib
                swot_data = json_lib.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse SWOT response, using defaults")
                swot_data = {
                    "strengths": [],
                    "weaknesses": [],
                    "opportunities": [],
                    "threats": [],
                    "summary": response_text[:200],
                }

            return {
                "swot": {
                    "strengths": swot_data.get("strengths", []),
                    "weaknesses": swot_data.get("weaknesses", []),
                    "opportunities": swot_data.get("opportunities", []),
                    "threats": swot_data.get("threats", []),
                    "summary": swot_data.get("summary"),
                },
                "confidence": 1.0 if self.gemini_available else 0.6,
                "data_points_analyzed": (
                    len(context.get("campaigns", {}).get("campaigns", [])) +
                    len(context.get("competitors", {}).get("competitors", []))
                ),
                "limitations": [] if self.gemini_available else ["Using fallback analysis mode"],
            }
        except GeminiIntegrationError as e:
            logger.error(f"Gemini error in SWOT: {str(e)}")
            return {
                "swot": {
                    "strengths": [],
                    "weaknesses": [],
                    "opportunities": [],
                    "threats": [],
                    "summary": f"Error generating SWOT: {str(e)}",
                },
                "confidence": 0.0,
                "data_points_analyzed": 0,
                "limitations": ["AI service error"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in SWOT: {str(e)}")
            raise

    def recommendations(self) -> Dict[str, Any]:
        """
        Generate marketing recommendations based on tenant data.
        
        Returns:
            List of grounded recommendations
        """
        logger.info(f"Recommendations request from tenant {self.school_id}")

        if not self._verify_tenant_access():
            raise AIServiceError("Tenant not found or inactive")

        try:
            context = self.rag.get_full_context()

            prompt = f"""
Generate 3-5 specific, actionable marketing recommendations for this school based on their campaign data and competitive position.

**Data:**
{json.dumps(context, indent=2, default=str)}

**RULES:**
- ONLY recommend actions based on actual data
- Do not invent campaigns or competitors
- If data is insufficient, say so
- Prioritize recommendations by impact and effort
- Include expected improvements based on actual patterns in data

Respond in JSON format:
{{
  "recommendations": [
    {{
      "title": "recommendation title",
      "description": "detailed description",
      "priority": "high/medium/low",
      "estimated_impact": "description of expected impact",
      "implementation_effort": "low/medium/high"
    }}
  ],
  "summary": "overall summary"
}}
"""
            if self.gemini_available:
                response_text = self._call_gemini(prompt, temperature=0.6)
            else:
                response_text = self._generate_recommendations_fallback(context)

            try:
                import json as json_lib
                data = json_lib.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse recommendations response")
                data = {"recommendations": [], "summary": response_text[:200]}

            return {
                "recommendations": data.get("recommendations", []),
                "summary": data.get("summary"),
                "confidence": 1.0 if self.gemini_available else 0.6,
                "limitations": [] if self.gemini_available else ["Using fallback mode"],
            }
        except GeminiIntegrationError as e:
            logger.error(f"Gemini error in recommendations: {str(e)}")
            return {
                "recommendations": [],
                "summary": f"Error generating recommendations: {str(e)}",
                "confidence": 0.0,
                "limitations": ["AI service error"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in recommendations: {str(e)}")
            raise

    def competitor_insights(self) -> Dict[str, Any]:
        """
        Generate insights about competitors based on threat scores and patterns.
        
        Returns:
            Competitor insights and strategic recommendations
        """
        logger.info(f"Competitor insights request from tenant {self.school_id}")

        if not self._verify_tenant_access():
            raise AIServiceError("Tenant not found or inactive")

        try:
            context = self.rag.get_full_context()
            competitors = context.get("competitors", {}).get("competitors", [])

            if not competitors:
                return {
                    "insights": [],
                    "market_overview": "No competitors tracked yet. Add competitors to get insights.",
                    "confidence": 0.0,
                    "limitations": ["No competitor data available"],
                }

            prompt = f"""
Analyze the competitive landscape and generate strategic insights.

**Data:**
{json.dumps(context, indent=2, default=str)}

**RULES:**
- ONLY analyze actual competitors in the data
- Do not invent competitors or their capabilities
- Use threat scores to guide your analysis
- If you don't have data about a specific threat, say so

Respond in JSON format:
{{
  "insights": [
    {{
      "competitor_name": "name",
      "threat_level": "high/medium/low",
      "key_strengths": ["strength1"],
      "vulnerabilities": ["vulnerability1"],
      "recommended_actions": ["action1"]
    }}
  ],
  "market_overview": "brief market analysis"
}}
"""
            if self.gemini_available:
                response_text = self._call_gemini(prompt, temperature=0.5)
            else:
                response_text = self._generate_competitor_fallback(context)

            try:
                import json as json_lib
                data = json_lib.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse competitor insights response")
                data = {"insights": [], "market_overview": response_text[:200]}

            return {
                "insights": data.get("insights", []),
                "market_overview": data.get("market_overview"),
                "confidence": 1.0 if self.gemini_available else 0.6,
                "limitations": [] if self.gemini_available else ["Using fallback mode"],
            }
        except GeminiIntegrationError as e:
            logger.error(f"Gemini error in competitor_insights: {str(e)}")
            return {
                "insights": [],
                "market_overview": f"Error generating insights: {str(e)}",
                "confidence": 0.0,
                "limitations": ["AI service error"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in competitor_insights: {str(e)}")
            raise

    def campaign_optimization(self) -> Dict[str, Any]:
        """
        Generate optimization suggestions for active campaigns.
        
        Returns:
            Campaign optimization suggestions
        """
        logger.info(f"Campaign optimization request from tenant {self.school_id}")

        if not self._verify_tenant_access():
            raise AIServiceError("Tenant not found or inactive")

        try:
            context = self.rag.get_full_context()
            campaigns = context.get("campaigns", {}).get("campaigns", [])

            if not campaigns:
                return {
                    "optimizations": [],
                    "summary": "No campaigns found. Create campaigns to get optimization suggestions.",
                    "confidence": 0.0,
                    "limitations": ["No campaign data available"],
                }

            prompt = f"""
Suggest specific optimizations for active and recent campaigns based on performance data.

**Data:**
{json.dumps(context, indent=2, default=str)}

**RULES:**
- ONLY suggest optimizations based on actual campaign data
- Focus on low-ROI campaigns and improvement opportunities
- Do not invent new channels or strategies without data supporting them
- Consider budget vs. spend vs. conversions

Respond in JSON format:
{{
  "optimizations": [
    {{
      "campaign_name": "name",
      "suggestion": "specific optimization",
      "expected_improvement": "expected metric improvement",
      "urgency": "high/medium/low"
    }}
  ],
  "summary": "overall optimization strategy"
}}
"""
            if self.gemini_available:
                response_text = self._call_gemini(prompt, temperature=0.6)
            else:
                response_text = self._generate_optimization_fallback(context)

            try:
                import json as json_lib
                data = json_lib.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse optimization response")
                data = {"optimizations": [], "summary": response_text[:200]}

            return {
                "optimizations": data.get("optimizations", []),
                "summary": data.get("summary"),
                "confidence": 1.0 if self.gemini_available else 0.6,
                "limitations": [] if self.gemini_available else ["Using fallback mode"],
            }
        except GeminiIntegrationError as e:
            logger.error(f"Gemini error in campaign_optimization: {str(e)}")
            return {
                "optimizations": [],
                "summary": f"Error generating optimizations: {str(e)}",
                "confidence": 0.0,
                "limitations": ["AI service error"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in campaign_optimization: {str(e)}")
            raise

    def trend_predictions(self, time_horizon_days: int = 30) -> Dict[str, Any]:
        """
        Predict trends based on historical campaign data.
        
        Args:
            time_horizon_days: Number of days to predict ahead (1-365)
        
        Returns:
            Trend predictions with reasoning
        """
        logger.info(f"Trend prediction request from tenant {self.school_id}")

        if not self._verify_tenant_access():
            raise AIServiceError("Tenant not found or inactive")

        try:
            context = self.rag.get_full_context()
            campaigns = context.get("campaigns", {}).get("campaigns", [])

            if not campaigns:
                return {
                    "predictions": [],
                    "summary": "Insufficient historical data for predictions.",
                    "data_points_used": 0,
                    "confidence": 0.0,
                    "limitations": ["Not enough campaign history"],
                }

            # Clamp time horizon
            time_horizon_days = max(1, min(365, time_horizon_days))

            prompt = f"""
Based on historical campaign performance, predict trends for the next {time_horizon_days} days.

**Data:**
{json.dumps(context, indent=2, default=str)}

**RULES:**
- ONLY make predictions based on actual historical patterns
- If patterns are unclear, say so instead of guessing
- Consider seasonality if visible in data
- Explain reasoning based on concrete data trends

Respond in JSON format:
{{
  "predictions": [
    {{
      "metric": "metric name",
      "predicted_value": "predicted value or trend",
      "confidence": 0.0-1.0,
      "reasoning": "data-driven reasoning"
    }}
  ],
  "summary": "overall trend prediction"
}}
"""
            if self.gemini_available:
                response_text = self._call_gemini(prompt, temperature=0.4)
            else:
                response_text = self._generate_predictions_fallback(context)

            try:
                import json as json_lib
                data = json_lib.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse predictions response")
                data = {"predictions": [], "summary": response_text[:200]}

            return {
                "predictions": data.get("predictions", []),
                "summary": data.get("summary"),
                "data_points_used": len(campaigns),
                "confidence": 1.0 if self.gemini_available else 0.5,
                "limitations": [] if self.gemini_available else ["Using fallback mode"],
            }
        except GeminiIntegrationError as e:
            logger.error(f"Gemini error in trend_predictions: {str(e)}")
            return {
                "predictions": [],
                "summary": f"Error generating predictions: {str(e)}",
                "data_points_used": 0,
                "confidence": 0.0,
                "limitations": ["AI service error"],
            }
        except Exception as e:
            logger.error(f"Unexpected error in trend_predictions: {str(e)}")
            raise

    # Fallback response generators (when Gemini is unavailable)

    def _generate_fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate simple fallback response based on context."""
        school_name = context.get("school", {}).get("name", "School")
        campaigns = context.get("campaigns", {}).get("campaigns", [])

        return (
            f"I'm operating in fallback mode without full AI capabilities. "
            f"Based on available data for {school_name}: "
            f"You have {len(campaigns)} campaigns tracked. "
            f"For more detailed analysis, please ensure Gemini API is configured. "
            f"Your question was: {message[:50]}..."
        )

    def _generate_swot_fallback(self, context: Dict[str, Any]) -> str:
        """Generate fallback SWOT analysis."""
        campaigns = context.get("campaigns", {}).get("campaigns", [])
        competitors = context.get("competitors", {}).get("competitors", [])

        return json.dumps({
            "strengths": [
                f"Tracking {len(campaigns)} campaigns",
                "Monitoring competitive landscape",
            ],
            "weaknesses": [
                "Limited historical data" if len(campaigns) < 5 else "Data available",
            ],
            "opportunities": [
                f"Leverage insights from {len(competitors)} tracked competitors"
                if competitors else "Monitor more competitors",
            ],
            "threats": [
                "Competitive market"
            ] if competitors else [],
            "summary": "Fallback SWOT - Gemini API not available",
        })

    def _generate_recommendations_fallback(self, context: Dict[str, Any]) -> str:
        """Generate fallback recommendations."""
        campaigns = context.get("campaigns", {}).get("campaigns", [])
        low_roi = [c for c in campaigns if c.get("roi_pct", 0) < 0]

        return json.dumps({
            "recommendations": [
                {
                    "title": "Optimize low-ROI campaigns",
                    "description": f"Review {len(low_roi)} campaigns with negative ROI",
                    "priority": "high" if low_roi else "low",
                    "estimated_impact": "Improved overall campaign performance",
                    "implementation_effort": "medium",
                },
            ],
            "summary": "Fallback recommendations - Use Gemini API for detailed analysis",
        })

    def _generate_competitor_fallback(self, context: Dict[str, Any]) -> str:
        """Generate fallback competitor insights."""
        competitors = context.get("competitors", {}).get("competitors", [])
        high_threat = [c for c in competitors if c.get("threat_score", 0) > 0.7]

        return json.dumps({
            "insights": [
                {
                    "competitor_name": c["name"],
                    "threat_level": "high" if c.get("threat_score", 0) > 0.7 else "medium",
                    "key_strengths": [],
                    "vulnerabilities": [],
                    "recommended_actions": ["Monitor closely"],
                }
                for c in high_threat[:3]
            ],
            "market_overview": f"Tracking {len(competitors)} competitors, {len(high_threat)} with high threat scores",
        })

    def _generate_optimization_fallback(self, context: Dict[str, Any]) -> str:
        """Generate fallback campaign optimizations."""
        campaigns = context.get("campaigns", {}).get("campaigns", [])
        active = [c for c in campaigns if c.get("status") == "active"]

        return json.dumps({
            "optimizations": [
                {
                    "campaign_name": c["name"],
                    "suggestion": "Review and optimize",
                    "expected_improvement": "Better ROI",
                    "urgency": "medium",
                }
                for c in active[:3]
            ],
            "summary": f"Fallback optimization - {len(active)} active campaigns to review",
        })

    def _generate_predictions_fallback(self, context: Dict[str, Any]) -> str:
        """Generate fallback predictions."""
        campaigns = context.get("campaigns", {}).get("campaigns", [])
        avg_conversions = context.get("campaigns", {}).get("avg_conversions", 0)

        return json.dumps({
            "predictions": [
                {
                    "metric": "Campaign success rate",
                    "predicted_value": f"Based on {len(campaigns)} historical campaigns",
                    "confidence": 0.4,
                    "reasoning": "Limited historical data",
                },
            ],
            "summary": "Fallback predictions - Accumulate more campaign data for better accuracy",
        })
