import redis
from datetime import timedelta
from typing import Any, Optional
import json
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=1,
            )
            self.redis.ping()  # Test connection
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except redis.ConnectionError:
            logger.warning("Could not connect to Redis, falling back to in-memory storage")
            self.redis = None
            self._memory_store = {}
            
        self.default_expiry = timedelta(hours=24)

    async def set_session(self, session_id: str, data: dict, expiry: Optional[timedelta] = None) -> None:
        """Store session data in Redis or memory"""
        expiry = expiry or self.default_expiry
        if self.redis:
            await self.redis.setex(
                f"session:{session_id}",
                expiry,
                json.dumps(data)
            )
        else:
            self._memory_store[f"session:{session_id}"] = {
                'data': data,
                'expiry': expiry
            }

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data from Redis or memory"""
        if self.redis:
            data = await self.redis.get(f"session:{session_id}")
            return json.loads(data) if data else None
        else:
            session = self._memory_store.get(f"session:{session_id}")
            return session['data'] if session else None

    async def delete_session(self, session_id: str) -> None:
        """Delete session data from Redis or memory"""
        if self.redis:
            await self.redis.delete(f"session:{session_id}")
        else:
            self._memory_store.pop(f"session:{session_id}", None)

    async def update_session(self, session_id: str, data: dict) -> None:
        """Update existing session data"""
        existing = await self.get_session(session_id)
        if existing:
            existing.update(data)
            await self.set_session(session_id, existing)

# Global session manager instance
session_manager = SessionManager()