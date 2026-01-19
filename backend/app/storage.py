from typing import Dict,Optional
from datetime import datetime


class EndpointStore:
    def __init__(self):
        self._endpoints: Dict[str, Dict[str, any]] = {}


    def create(self,endpoint_id: str, name:Optional[str]=None) -> Dict:
        endpoint_data: Dict = {
                "id": endpoint_id,
                "name": name,
                "created_at": datetime.now(),
                "request_count": 0
        }

        self._endpoints[endpoint_id] = endpoint_data

        return endpoint_data


    def get(self,endpoint_id: str) -> Optional[Dict]:
        return self._endpoints.get(endpoint_id)


    def increment_count(self,endpoint_id: str) -> None:
        if endpoint_id in self._endpoints:
            self._endpoints[endpoint_id]["request_count"] += 1


endpoint_store = EndpointStore()

