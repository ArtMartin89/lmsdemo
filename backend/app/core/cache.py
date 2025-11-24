import json
from typing import Optional, Any, Callable
import redis.asyncio as redis


class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            return await self.redis.get(key)
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: int = 3600
    ) -> bool:
        """Set value in cache with expiration"""
        try:
            return await self.redis.setex(key, expire, value)
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.redis.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0
    
    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        expire: int = 3600
    ) -> Any:
        """Get from cache or fetch and cache"""
        cached = await self.get(key)
        if cached:
            return json.loads(cached)
        
        value = await fetch_func()
        await self.set(key, json.dumps(value, default=str), expire)
        return value

