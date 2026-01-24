import json
from typing import Optional, Dict, Any
from anthropic import Anthropic
from core.config import settings


class AIService:
    def __init__(self):
        if settings.ANTHROPIC_API_KEY and settings.AI_ENABLED:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.enabled = True
            print("🤖 AI Service enabled")
        else:
            self.client = None
            self.enabled = False
            if not settings.ANTHROPIC_API_KEY:
                print("⚠️  AI Service disabled - no API key configured")
            else:
                print("⚠️  AI Service disabled - AI_ENABLED=false")

    async def generate_mock_response(
            self,
            webhook_data: Dict[str, Any],
            endpoint_id: str,
            ip_address: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None

        from middleware.rate_limiter import rate_limiter
        from middleware.usage_tracker import usage_tracker

        if not rate_limiter.check_endpoint_limit(
                endpoint_id,
                max_calls=settings.AI_CALLS_PER_ENDPOINT_PER_HOUR
        ):
            remaining = rate_limiter.get_remaining_calls(
                endpoint_id,
                settings.AI_CALLS_PER_ENDPOINT_PER_HOUR
            )
            print(f"⚠️  Rate limit exceeded for endpoint {endpoint_id}")
            return {
                "error": "AI rate limit exceeded",
                "message": f"This endpoint has reached its AI generation limit ({settings.AI_CALLS_PER_ENDPOINT_PER_HOUR}/hour). Remaining: {remaining}",
                "rate_limited": True,
                "limit": settings.AI_CALLS_PER_ENDPOINT_PER_HOUR,
                "remaining": remaining
            }

        if ip_address and not rate_limiter.check_ip_limit(
                ip_address,
                max_calls=settings.AI_CALLS_PER_IP_PER_HOUR
        ):
            print(f"⚠️  Rate limit exceeded for IP {ip_address}")
            return {
                "error": "AI rate limit exceeded",
                "message": f"Too many AI requests from your IP ({settings.AI_CALLS_PER_IP_PER_HOUR}/hour). Try again later.",
                "rate_limited": True,
                "limit": settings.AI_CALLS_PER_IP_PER_HOUR
            }

        try:
            method = webhook_data.get("method", "POST")
            body = webhook_data.get("body_raw", "")
            headers = webhook_data.get("headers", {})

            prompt = self._build_prompt(method, body, headers)

            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=settings.MAX_AI_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text
            mock_response = self._extract_json(response_text)

            tokens_used = len(response_text) // 4
            usage_tracker.track_call(tokens_used)

            stats = usage_tracker.get_stats()
            print(f"✅ AI response generated (tokens: ~{tokens_used})")
            print(
                f"📊 Total AI calls: {stats['total_calls']} | Today: {stats['today_calls']} | Cost: ${stats['estimated_cost']:.4f}")

            return {
                "mock_response": mock_response,
                "ai_model": "claude-sonnet-4-5-20250929",
                "generated_at": webhook_data.get("timestamp"),
                "tokens_used": tokens_used
            }

        except Exception as e:
            print(f"❌ AI Service error: {e}")
            return {
                "error": "AI generation failed",
                "message": str(e)
            }

    def _build_prompt(self, method: str, body: str, headers: Dict) -> str:
        return f"""You are an API mock response generator. Analyze this webhook request and generate an appropriate JSON response.

REQUEST METHOD: {method}
REQUEST BODY: {body if body else "Empty"}

Generate a realistic mock response that:
1. Matches the request context (e.g., payment webhooks get payment confirmations)
2. Includes appropriate status codes and messages
3. Contains realistic IDs, timestamps, and data
4. Follows REST API best practices
5. Is CONCISE - keep response under 200 characters when possible

Respond ONLY with valid JSON. No explanations, no markdown, just the JSON object.

Example for payment webhook:
{{
  "status": "success",
  "transaction_id": "tx_abc123",
  "amount": 100.00,
  "currency": "USD",
  "message": "Payment processed successfully"
}}

Now generate a mock response for the above request:"""

    def _extract_json(self, text: str) -> Dict[str, Any]:
        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"message": text, "raw": True}


ai_service = AIService()