from pydantic import BaseModel
from typing import Optional


class LessonResponse(BaseModel):
    status: str
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


