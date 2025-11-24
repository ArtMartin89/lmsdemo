from typing import Optional, Dict, Any
import json

from app.core.cache import CacheService
from app.core.storage import StorageService


class ContentService:
    def __init__(self, cache_service: CacheService, storage_service: StorageService):
        self.cache = cache_service
        self.storage = storage_service
    
    async def get_lesson_content(
        self, 
        module_id: str, 
        lesson_number: int
    ) -> Optional[Dict[str, Any]]:
        """Retrieve lesson content from cache or storage"""
        cache_key = f"lesson:{module_id}:{lesson_number}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Fetch from storage
        lesson_data = await self.storage.get_lesson_content(module_id, lesson_number)
        
        if lesson_data:
            # Cache for 1 hour
            await self.cache.set(cache_key, json.dumps(lesson_data, default=str), expire=3600)
        
        return lesson_data
    
    async def get_test_questions(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve test questions from storage"""
        cache_key = f"test_questions:{module_id}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        questions = await self.storage.get_test_questions(module_id)
        
        if questions:
            # Cache for 1 hour
            await self.cache.set(cache_key, json.dumps(questions, default=str), expire=3600)
        
        return questions
    
    async def get_correct_answers(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve correct answers (internal use only)"""
        return await self.storage.get_correct_answers(module_id)


