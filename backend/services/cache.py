import time
import asyncio
from typing import Dict, Any, Optional, Tuple

class InMemoryTTLCache:
    def __init__(self, default_ttl_seconds: int = 600):
        """
        In-memory cache with Time-To-Live (TTL) eviction.
        Default TTL: 600 seconds (10 minutes).
        """
        self.default_ttl = default_ttl_seconds
        # Storage: key -> (value, expiry_timestamp)
        self._cache: Dict[Tuple[str, str], Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    def _make_key(self, role: str, city: str) -> Tuple[str, str]:
        return (role.strip().lower(), city.strip().lower())

    async def get(self, role: str, city: str) -> Optional[Any]:
        """
        Retrieve a value from the cache. Returns None if not found or expired.
        """
        key = self._make_key(role, city)
        async with self._lock:
            if key not in self._cache:
                return None
            
            val, expiry = self._cache[key]
            if time.time() > expiry:
                # Expired, clean it up
                del self._cache[key]
                return None
            
            return val

    async def set(self, role: str, city: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Store a value in the cache with an optional override for TTL.
        """
        key = self._make_key(role, city)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiry = time.time() + ttl
        async with self._lock:
            self._cache[key] = (value, expiry)

    async def clear(self) -> None:
        """
        Clear the cache entirely.
        """
        async with self._lock:
            self._cache.clear()
