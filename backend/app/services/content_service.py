from typing import Optional, Dict, Any
import json
from uuid import UUID

from app.core.cache import CacheService
from app.core.storage import StorageService
from app.crud.module import get_module
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession


class ContentService:
    def __init__(self, cache_service: CacheService, storage_service: StorageService):
        self.cache = cache_service
        self.storage = storage_service
    
    async def get_lesson_for_user(
        self,
        module_id: str,
        lesson_id: str,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get lesson content for user (with course_id resolution)"""
        # Get module to get course_id
        module = await get_module(db, module_id)
        if not module:
            return None
        
        course_id = module.course_id
        cache_key = f"lesson:{course_id}:{module_id}:{lesson_id}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Fetch from storage
        lesson_data = await self.storage.get_lesson_content(course_id, module_id, lesson_id)
        
        if lesson_data:
            # Get files
            files = await self.storage.list_lesson_files(course_id, module_id, lesson_id)
            lesson_data["files"] = files
            
            # Cache for 1 hour
            await self.cache.set(cache_key, json.dumps(lesson_data, default=str), expire=3600)
        
        return lesson_data
    
    async def get_lesson_content(
        self, 
        module_id: str, 
        lesson_number: int,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Retrieve lesson content from cache or storage (backward compatibility)"""
        # Get module to get course_id
        module = await get_module(db, module_id)
        if not module:
            return None
        
        course_id = module.course_id
        
        # Construct lesson_id from module_id and lesson_number
        lesson_id = f"{module_id}_Lesson_{lesson_number:02d}"
        
        return await self.get_lesson_for_user(module_id, lesson_id, db)
    
    async def validate_lesson_access(
        self,
        module_id: str,
        lesson_id: str,
        user_id: UUID,
        db: AsyncSession
    ) -> bool:
        """Validate that user has access to lesson"""
        # For now, if module exists and is active, user has access
        # Can be extended with additional checks
        module = await get_module(db, module_id)
        if not module or not module.is_active:
            return False
        return True
    
    async def get_next_lesson(
        self,
        module_id: str,
        current_lesson_number: int,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get next lesson in sequence"""
        next_lesson_number = current_lesson_number + 1
        return await self.get_lesson_content(module_id, next_lesson_number, db)
    
    async def get_test_questions(self, module_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Retrieve test questions from storage"""
        # Get module to get course_id
        module = await get_module(db, module_id)
        if not module:
            return None
        
        course_id = module.course_id
        cache_key = f"test_questions:{course_id}:{module_id}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        questions = await self.storage.get_test_questions(course_id, module_id)
        
        if questions:
            # Cache for 1 hour
            await self.cache.set(cache_key, json.dumps(questions, default=str), expire=3600)
        
        return questions
    
    async def get_test_settings(self, module_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Retrieve test settings from storage"""
        # Get module to get course_id
        module = await get_module(db, module_id)
        if not module:
            return None
        
        course_id = module.course_id
        cache_key = f"test_settings:{course_id}:{module_id}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        settings = await self.storage.get_test_settings(course_id, module_id)
        
        if settings:
            # Cache for 1 hour
            await self.cache.set(cache_key, json.dumps(settings, default=str), expire=3600)
        
        return settings
    
    async def get_correct_answers(self, module_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Retrieve correct answers (internal use only)"""
        # In new structure, answers are in questions.json
        questions = await self.get_test_questions(module_id, db)
        if not questions:
            return None
        
        # Extract correct answers from questions
        answers = {}
        for question in questions.get("questions", []):
            answers[question["id"]] = question.get("correct_answer")
        
        return answers
