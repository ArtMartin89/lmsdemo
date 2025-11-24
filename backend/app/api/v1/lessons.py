from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.progress import ProgressStatus
from app.services.content_service import ContentService
from app.services.progress_service import ProgressService
from app.core.storage import StorageService
from app.schemas.lesson import LessonContentResponse
from app.crud.module import get_module
from app.crud.lesson import get_lesson_by_module_and_number
from app.dependencies import (
    get_content_service,
    get_progress_service,
    get_storage_service
)

router = APIRouter()


@router.get("/modules/{module_id}/lessons/{lesson_number}", response_model=LessonContentResponse)
async def get_lesson(
    module_id: str,
    lesson_number: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get lesson content"""
    # Get lesson from DB
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson or not lesson.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson {lesson_number} not found"
        )
    
    # Get lesson content
    lesson_data = await content_service.get_lesson_content(module_id, lesson_number, db)
    if not lesson_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson content not found"
        )
    
    # Get user progress
    progress = await progress_service.get_user_progress(current_user.id, module_id)
    
    progress_percentage = None
    if progress:
        progress_percentage = int((lesson_number / progress.total_lessons) * 100)
    
    return LessonContentResponse(
        status="success",
        lesson_id=lesson.id,
        lesson_number=lesson_number,
        total_lessons=progress.total_lessons if progress else None,
        content=lesson_data.get("content"),
        content_type=lesson_data.get("content_type", "markdown"),
        module_id=module_id,
        progress_percentage=progress_percentage,
        files=lesson_data.get("files", {})
    )


@router.get("/modules/{module_id}/lessons/{lesson_number}/files/{file_type}/{filename}")
async def get_lesson_file(
    module_id: str,
    lesson_number: int,
    file_type: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage_service: StorageService = Depends(get_storage_service)
):
    """Download lesson file"""
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Get lesson to get lesson_id
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get file
    file_content = await storage_service.get_file(
        module.course_id,
        module_id,
        lesson.id,
        file_type,
        filename
    )
    
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine content type from filename
    content_type = "application/octet-stream"
    if filename.endswith((".mp3", ".wav", ".ogg")):
        content_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    elif filename.endswith((".mp4", ".webm", ".mov")):
        content_type = "video/mp4" if filename.endswith(".mp4") else "video/webm"
    elif filename.endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif filename.endswith(".png"):
        content_type = "image/png"
    elif filename.endswith(".gif"):
        content_type = "image/gif"
    elif filename.endswith(".pdf"):
        content_type = "application/pdf"
    
    return Response(
        content=file_content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )


@router.post("/modules/{module_id}/next", response_model=LessonContentResponse)
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
        return LessonContentResponse(
            status="completed",
            message="Module already completed",
            test_result_id=str(progress.test_results[-1].id) if progress.test_results else None
        )
    
    # Check if all lessons completed -> start test
    if progress.current_lesson >= progress.total_lessons:
        await progress_service.update_status(progress.id, ProgressStatus.TESTING)
        
        test_questions = await content_service.get_test_questions(module_id, db)
        
        return LessonContentResponse(
            status="module_completed",
            message="All lessons completed. Ready for test.",
            test_available=True,
            test_questions=test_questions
        )
    
    # Get next lesson
    next_lesson_number = progress.current_lesson + 1
    lesson_content = await content_service.get_lesson_content(
        module_id, next_lesson_number, db
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
    
    return LessonContentResponse(
        status="success",
        lesson_number=next_lesson_number,
        total_lessons=progress.total_lessons,
        content=lesson_content.get("content"),
        content_type="markdown",
        module_id=module_id,
        progress_percentage=progress_percentage,
        files=lesson_content.get("files", {})
    )
