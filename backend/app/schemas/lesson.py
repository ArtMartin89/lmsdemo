from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LessonBase(BaseModel):
    id: str
    module_id: str
    lesson_number: int
    title: str
    order_index: int


class LessonCreate(BaseModel):
    id: str
    module_id: str
    lesson_number: int
    title: str
    order_index: int
    is_active: bool = True


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    lesson_number: Optional[int] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class LessonResponse(LessonBase):
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Response for lesson content (for users)
class LessonContentResponse(BaseModel):
    status: str
    lesson_id: Optional[str] = None
    lesson_number: Optional[int] = None
    total_lessons: Optional[int] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    module_id: Optional[str] = None
    progress_percentage: Optional[int] = None
    message: Optional[str] = None
    test_available: Optional[bool] = None
    test_questions: Optional[dict] = None
    test_result_id: Optional[str] = None
    files: Optional[dict] = None  # {audio: [], video: [], images: [], attachments: []}


