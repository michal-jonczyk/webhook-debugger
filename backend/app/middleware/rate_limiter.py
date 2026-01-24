from datetime import datetime, timedelta
from typing import Dict
from collections import defaultdict


class RateLimiter:
    def __init__(self):
        self.ai_calls: Dict[str, list] = defaultdict(list)
        self.ip_calls: Dict[str, list] = defaultdict(list)

    def check_endpoint_limit(
            self,
            endpoint_id: str,
            max_calls: int = 10,
            window_minutes: int = 60
    ) -> bool:
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        self.ai_calls[endpoint_id] = [
            ts for ts in self.ai_calls[endpoint_id]
            if ts > window_start
        ]

        if len(self.ai_calls[endpoint_id]) >= max_calls:
            return False

        self.ai_calls[endpoint_id].append(now)
        return True

    def check_ip_limit(
            self,
            ip_address: str,
            max_calls: int = 20,
            window_minutes: int = 60
    ) -> bool:
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        self.ip_calls[ip_address] = [
            ts for ts in self.ip_calls[ip_address]
            if ts > window_start
        ]

        if len(self.ip_calls[ip_address]) >= max_calls:
            return False

        self.ip_calls[ip_address].append(now)
        return True

    def get_remaining_calls(self, endpoint_id: str, max_calls: int = 10) -> int:
        now = datetime.now()
        window_start = now - timedelta(minutes=60)

        self.ai_calls[endpoint_id] = [
            ts for ts in self.ai_calls[endpoint_id]
            if ts > window_start
        ]

        return max(0, max_calls - len(self.ai_calls[endpoint_id]))


rate_limiter = RateLimiter()