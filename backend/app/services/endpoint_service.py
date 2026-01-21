import uuid
from typing import Optional,Dict

from storage.store import endpoint_store
from core.config import settings


class EndpointService:
    def __init__(self):
        self.store = endpoint_store
        self.config = settings


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

endpoint_service = EndpointService()