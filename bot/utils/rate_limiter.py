"""
Simple per-user in-memory sliding window rate limiter.
"""

import time
from typing import Dict, List


class UserRateLimiter:
    """Rate limiter to prevent user flood/spam."""

    def __init__(self, max_requests: int = 15, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: Dict[int, List[float]] = {}

    def is_rate_limited(self, user_id: int) -> bool:
        """Check if user has exceeded request quota."""
        now = time.time()
        cutoff = now - self.window_seconds

        if user_id not in self._timestamps:
            self._timestamps[user_id] = []

        # Filter out timestamps older than the sliding window
        self._timestamps[user_id] = [
            ts for ts in self._timestamps[user_id] if ts > cutoff
        ]

        if len(self._timestamps[user_id]) >= self.max_requests:
            return True

        self._timestamps[user_id].append(now)
        return False


rate_limiter = UserRateLimiter()
