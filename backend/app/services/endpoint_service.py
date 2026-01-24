import uuid
import json
from typing import Optional, Dict
from datetime import datetime
from fastapi import HTTPException, Request

from storage.store import endpoint_store
from core.config import settings
from schemas.endpoint import WebhookRequest
from services.ai_service import ai_service


class EndpointService:
    def __init__(self):
        self.store = endpoint_store
        self.config = settings
        self.ws_manager = None

    def set_websocket_manager(self, manager):
        self.ws_manager = manager

    def create_endpoint(self, name: Optional[str] = None) -> Dict:
        endpoint_id = str(uuid.uuid4())
        endpoint_data = self.store.create(
            endpoint_id=endpoint_id,
            name=name
        )

        webhook_url = f"{self.config.BASE_URL}/w/{endpoint_id}"

        return {
            "id": endpoint_data["id"],
            "url": webhook_url,
            "name": endpoint_data["name"],
            "created_at": endpoint_data["created_at"]
        }

    def get_endpoint(self, endpoint_id: str) -> Dict:
        endpoint_data = self.store.get(endpoint_id)

        if not endpoint_data:
            return None

        webhook_url = f"{self.config.BASE_URL}/w/{endpoint_id}"

        return {
            "id": endpoint_data["id"],
            "url": webhook_url,
            "name": endpoint_data["name"],
            "created_at": endpoint_data["created_at"]
        }

    async def receive_webhook(
            self,
            endpoint_id: str,
            request: Request,
    ) -> Dict:
        endpoint_data = self.store.get(endpoint_id)
        if not endpoint_data:
            raise HTTPException(status_code=404, detail="Endpoint not found")

        body_raw = await request.body()
        body_text = body_raw.decode("utf-8")

        body_json = None
        try:
            if body_text:
                body_json = json.loads(body_text)
        except json.decoder.JSONDecodeError:
            pass

        client_ip = request.client.host if request.client else None

        request_id = str(uuid.uuid4())

        webhook_data = {
            "id": request_id,
            "timestamp": datetime.now(),
            "method": request.method,
            "headers": dict(request.headers),
            "body_raw": body_text,
            "body_json": body_json,
            "content_type": request.headers.get("content-type"),
            "content_length": len(body_raw),
            "ip_address": client_ip,
            "query_params": dict(request.query_params)
        }

        ai_mock = await ai_service.generate_mock_response(
            webhook_data,
            endpoint_id=endpoint_id,
            ip_address=client_ip
        )

        if ai_mock:
            webhook_data["ai_mock_response"] = ai_mock
            if not ai_mock.get("rate_limited") and not ai_mock.get("error"):
                print(f"🤖 AI generated mock response for {request_id}")
            elif ai_mock.get("rate_limited"):
                print(f"⚠️  Rate limit hit for {request_id}")

        self.store.add_request(endpoint_id, webhook_data)

        if self.ws_manager:
            webhook_data_serializable = {
                **webhook_data,
                "timestamp": webhook_data["timestamp"].isoformat()
            }

            if "ai_mock_response" in webhook_data_serializable:
                ai_data = webhook_data_serializable["ai_mock_response"]
                if "generated_at" in ai_data:
                    if hasattr(ai_data["generated_at"], "isoformat"):
                        ai_data["generated_at"] = ai_data["generated_at"].isoformat()

            await self.ws_manager.broadcast_new_request(
                endpoint_id,
                webhook_data_serializable
            )

        return {
            "status": "received",
            "endpoint_id": endpoint_id,
            "request_id": request_id,
            "received_at": datetime.now().isoformat(),
            "total_requests": endpoint_data["request_count"],
            "ai_mock_response": ai_mock
        }


endpoint_service = EndpointService()