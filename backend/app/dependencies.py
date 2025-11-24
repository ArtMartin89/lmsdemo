from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.db.session import get_db
from app.config import settings
from app.core.cache import CacheService
from app.core.storage import StorageService
from app.services.content_service import ContentService
from app.services.test_service import TestGradingService
from app.services.progress_service import ProgressService


# Redis connection (singleton pattern)
_redis_client: redis.Redis = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            print(f"Warning: Redis connection failed: {e}")
            # Create a dummy client that won't crash
            _redis_client = redis.from_url("redis://localhost:6379/0", encoding="utf-8", decode_responses=True)
    return _redis_client


def get_cache_service(redis_client: redis.Redis = Depends(get_redis)) -> CacheService:
    return CacheService(redis_client)


def get_storage_service() -> StorageService:
    return StorageService()


def get_content_service(
    cache_service: CacheService = Depends(get_cache_service),
    storage_service: StorageService = Depends(get_storage_service)
) -> ContentService:
    return ContentService(cache_service, storage_service)


def get_grading_service() -> TestGradingService:
    return TestGradingService()


def get_progress_service(db: AsyncSession = Depends(get_db)) -> ProgressService:
    return ProgressService(db)

