import redis.asyncio as redis
from typing import Optional, Any
import json
from datetime import timedelta

from app.core.config import settings


class RedisCache:
    """Redis cache manager"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,  # Short timeout to fail fast
                socket_timeout=2
            )
            # Test connection with explicit timeout
            import asyncio
            async with asyncio.timeout(3):
                await self.redis_client.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        value = await self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300  # 5 minutes default
    ):
        """Set value in cache"""
        if not self.redis_client:
            return
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        await self.redis_client.setex(
            key,
            timedelta(seconds=expire),
            value
        )
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return
        
        await self.redis_client.delete(key)
    
    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return
        
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis_client:
            return False
        
        return await self.redis_client.exists(key) > 0


# Global cache instance
cache = RedisCache()


# Dependency for FastAPI
async def get_cache() -> RedisCache:
    return cache
