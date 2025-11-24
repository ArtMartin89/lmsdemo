from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.models.progress import UserProgress, ProgressStatus
from app.crud.progress import (
    get_user_progress as crud_get_user_progress,
    create_user_progress as crud_create_user_progress,
    update_current_lesson as crud_update_current_lesson,
    update_status as crud_update_status
)


class ProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_progress(
        self,
        user_id: UUID,
        module_id: str
    ) -> Optional[UserProgress]:
        return await crud_get_user_progress(self.db, user_id, module_id)
    
    async def create_user_progress(
        self,
        user_id: UUID,
        module_id: str,
        total_lessons: int
    ) -> UserProgress:
        return await crud_create_user_progress(
            self.db, user_id, module_id, total_lessons
        )
    
    async def update_current_lesson(
        self,
        progress_id: UUID,
        lesson_number: int
    ) -> UserProgress:
        return await crud_update_current_lesson(
            self.db, progress_id, lesson_number
        )
    
    async def update_status(
        self,
        progress_id: UUID,
        status: ProgressStatus
    ) -> UserProgress:
        return await crud_update_status(self.db, progress_id, status)


