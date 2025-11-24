from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.progress import ProgressStatus
from app.services.content_service import ContentService
from app.services.progress_service import ProgressService
from app.schemas.lesson import LessonResponse
from app.dependencies import (
    get_content_service,
    get_progress_service
)

router = APIRouter()


@router.post("/modules/{module_id}/next", response_model=LessonResponse)
async def get_next_lesson(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get next lesson in sequence or transition to test"""
    # Get user progress
    progress = await progress_service.get_user_progress(
        current_user.id, module_id
    )
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not started. Please start the module first."
        )
    
    # Check if module is completed
    if progress.status == ProgressStatus.COMPLETED:
        return LessonResponse(
            status="completed",
            message="Module already completed",
            test_result_id=str(progress.test_results[-1].id) if progress.test_results else None
        )
    
    # Check if all lessons completed -> start test
    if progress.current_lesson >= progress.total_lessons:
        await progress_service.update_status(progress.id, ProgressStatus.TESTING)
        
        test_questions = await content_service.get_test_questions(module_id)
        
        return LessonResponse(
            status="module_completed",
            message="All lessons completed. Ready for test.",
            test_available=True,
            test_questions=test_questions
        )
    
    # Get next lesson
    next_lesson_number = progress.current_lesson + 1
    lesson_content = await content_service.get_lesson_content(
        module_id, next_lesson_number
    )
    
    if not lesson_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson {next_lesson_number} not found"
        )
    
    # Update progress
    await progress_service.update_current_lesson(
        progress.id, next_lesson_number
    )
    
    progress_percentage = int((next_lesson_number / progress.total_lessons) * 100)
    
    return LessonResponse(
        status="success",
        lesson_number=next_lesson_number,
        total_lessons=progress.total_lessons,
        content=lesson_content["content"],
        content_type="markdown",
        module_id=module_id,
        progress_percentage=progress_percentage
    )


