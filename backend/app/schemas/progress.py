from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.progress import ProgressStatus


class ProgressResponse(BaseModel):
    module_id: str
    current_lesson: int
    total_lessons: int
    status: ProgressStatus
    progress_percentage: int
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OverallProgressResponse(BaseModel):
    total_modules: int
    completed_modules: int
    in_progress_modules: int
    average_grade: Optional[float] = None
    modules: List[ProgressResponse]


