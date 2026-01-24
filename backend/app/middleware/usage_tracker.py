from datetime import datetime
from collections import defaultdict


class UsageTracker:
    def __init__(self):
        self.total_ai_calls = 0
        self.daily_calls = defaultdict(int)
        self.estimated_cost = 0.0

    def track_call(self, tokens_used: int = 512):
        self.total_ai_calls += 1
        today = datetime.now().date().isoformat()
        self.daily_calls[today] += 1

        cost_per_token = 0.000003
        call_cost = tokens_used * cost_per_token
        self.estimated_cost += call_cost

        if self.daily_calls[today] > 100:
            print(f"🚨 WARNING: {self.daily_calls[today]} AI calls today!")
            print(f"💰 Estimated cost today: ${self.daily_calls[today] * 0.003:.2f}")

    def get_stats(self):
        today = datetime.now().date().isoformat()
        return {
            "total_calls": self.total_ai_calls,
            "today_calls": self.daily_calls[today],
            "estimated_cost": round(self.estimated_cost, 4)
        }


usage_tracker = UsageTracker()