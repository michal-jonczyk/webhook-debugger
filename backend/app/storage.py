from typing import Dict,Optional,List
from datetime import datetime


class EndpointStore:
    def __init__(self):
        self._endpoints: Dict[str, Dict[str, any]] = {}
        self.MAX_REQUESTS_PER_ENDPOINT = 100


    def create(self,endpoint_id: str, name:Optional[str]=None) -> Dict:
        endpoint_data: Dict = {
                "id": endpoint_id,
                "name": name,
                "created_at": datetime.now(),
                "request_count": 0,
                "requests": []
        }

        self._endpoints[endpoint_id] = endpoint_data

        return endpoint_data


    def get(self,endpoint_id: str) -> Optional[Dict]:
        return self._endpoints.get(endpoint_id)


    def increment_count(self,endpoint_id: str) -> None:
        if endpoint_id in self._endpoints:
            self._endpoints[endpoint_id]["request_count"] += 1


    def add_request(self,endpoint_id: str, request_data: Dict) -> bool:
        if endpoint_id not in self._endpoints:
            return False

        requests = self._endpoints[endpoint_id]["requests"]

        if len(requests) >= self.MAX_REQUESTS_PER_ENDPOINT:
            requests.pop(0)

        requests.append(request_data)
        self.increment_count(endpoint_id)
        return True


endpoint_store = EndpointStore()

