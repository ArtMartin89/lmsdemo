from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import io

from app.core.security import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.crud.course import (
    get_all_courses, get_course, create_course,
    update_course, delete_course
)
from app.crud.module import (
    get_all_modules, get_module, create_module, 
    update_module, delete_module
)
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseWithModules
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse
from app.schemas.lesson import LessonResponse
from app.core.storage import StorageService
from app.dependencies import get_storage_service
from uuid import UUID

router = APIRouter()


# Course Management
@router.get("/courses", response_model=List[CourseResponse])
async def admin_list_courses(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """List all courses (admin only)"""
    courses = await get_all_courses(db, include_inactive=True)
    # Convert to response models to ensure proper serialization
    result = []
    for course in courses:
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description or None,
            "order_index": course.order_index,
            "is_active": course.is_active,
            "created_at": course.created_at,
            "updated_at": course.updated_at
        }
        result.append(CourseResponse(**course_dict))
    return result


@router.get("/courses/{course_id}", response_model=CourseWithModules)
async def admin_get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get course with modules (admin only)"""
    from app.crud.module import get_all_modules
    course = await get_course(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get modules for this course
    course_modules = await get_all_modules(db, include_inactive=True, course_id=course_id)
    
    course_dict = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "order_index": course.order_index,
        "is_active": course.is_active,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
        "modules": course_modules
    }
    return course_dict


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Create a new course (admin only)"""
    course = await create_course(db, course_data.dict())
    
    # Save course metadata to storage
    metadata = {
        "course_id": str(course.id),
        "title": course.title,
        "description": course.description or "",
        "order_index": course.order_index,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None,
        "settings": {
            "completion_certificate": True,
            "min_completion_percentage": 80
        }
    }
    await storage_service.save_course_metadata(course.id, metadata)
    
    # Return properly serialized course
    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        order_index=course.order_index,
        is_active=course.is_active,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def admin_update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Update course (admin only)"""
    course = await update_course(db, course_id, course_data.dict(exclude_unset=True))
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Update course metadata in storage
    metadata = {
        "course_id": str(course.id),
        "title": course.title,
        "description": course.description or "",
        "order_index": course.order_index,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None,
        "settings": {
            "completion_certificate": True,
            "min_completion_percentage": 80
        }
    }
    await storage_service.save_course_metadata(course.id, metadata)
    
    # Return properly serialized course
    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        order_index=course.order_index,
        is_active=course.is_active,
        created_at=course.created_at,
        updated_at=course.updated_at
    )


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete course (admin only)"""
    success = await delete_course(db, course_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return None


# Module Management
@router.get("/modules", response_model=List[ModuleResponse])
async def admin_list_modules(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """List all modules (admin only)"""
    modules = await get_all_modules(db, include_inactive=True)
    return modules


@router.post("/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_module(
    module_data: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Create a new module (admin only)"""
    # Check if module already exists
    existing = await get_module(db, module_data.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module with this ID already exists"
        )
    
    module = await create_module(db, module_data.dict())
    return module


@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def admin_get_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get module details (admin only)"""
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def admin_update_module(
    module_id: str,
    module_data: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Update module (admin only)"""
    module = await update_module(db, module_id, module_data.dict(exclude_unset=True))
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete module (admin only)"""
    success = await delete_module(db, module_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return None


# Lesson Management
@router.get("/modules/{module_id}/lessons", response_model=List[dict])
async def admin_list_lessons(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """List all lessons for a module (admin only)"""
    from app.crud.lesson import get_all_lessons
    from app.schemas.lesson import LessonResponse
    
    lessons = await get_all_lessons(db, module_id=module_id, include_inactive=True)
    return [LessonResponse.model_validate(lesson).dict() for lesson in lessons]


@router.get("/modules/{module_id}/lessons/{lesson_number}")
async def admin_get_lesson(
    module_id: str,
    lesson_number: int,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get lesson for editing (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number
    from app.crud.module import get_module
    
    # Get lesson from DB
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Get lesson content
    content = await storage_service.get_lesson_content(
        module.course_id, module_id, lesson.id
    )
    
    # If lesson doesn't exist, return empty content
    if not content:
        content = {
            "lesson_id": lesson.id,
            "module_id": module_id,
            "lesson_number": lesson_number,
            "content": "",
            "content_type": "markdown"
        }
    
    # Get list of files
    files = await storage_service.list_lesson_files(
        module.course_id, module_id, lesson.id
    )
    content["files"] = files
    content["lesson"] = LessonResponse.model_validate(lesson).dict()
    
    return content


@router.post("/modules/{module_id}/lessons", response_model=dict, status_code=status.HTTP_201_CREATED)
async def admin_create_lesson(
    module_id: str,
    lesson_data: dict,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Create a new lesson (admin only)"""
    from app.crud.lesson import create_lesson, get_lesson
    from app.crud.module import get_module
    from app.schemas.lesson import LessonCreate
    
    # Check if module exists
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if lesson already exists
    existing = await get_lesson(db, lesson_data.get("id"))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson with this ID already exists"
        )
    
    # Set module_id
    lesson_data["module_id"] = module_id
    
    lesson = await create_lesson(db, lesson_data)
    return LessonResponse.model_validate(lesson).dict()


@router.put("/modules/{module_id}/lessons/{lesson_number}", response_model=dict)
async def admin_update_lesson(
    module_id: str,
    lesson_number: int,
    lesson_data: dict,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Update lesson (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number, update_lesson
    from app.schemas.lesson import LessonUpdate, LessonResponse
    
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    updated_lesson = await update_lesson(db, lesson.id, lesson_data)
    if not updated_lesson:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lesson"
        )
    
    return LessonResponse.model_validate(updated_lesson).dict()


@router.delete("/modules/{module_id}/lessons/{lesson_number}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_lesson(
    module_id: str,
    lesson_number: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete lesson (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number, delete_lesson
    
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    success = await delete_lesson(db, lesson.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete lesson"
        )
    return None


@router.post("/modules/{module_id}/lessons/{lesson_number}/files")
async def admin_upload_file(
    module_id: str,
    lesson_number: int,
    file_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Upload a file for a lesson (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number
    from app.crud.module import get_module
    
    # Validate file type
    valid_types = ["audio", "video", "images", "attachments"]
    if file_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Must be one of: {valid_types}"
        )
    
    # Get lesson
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Save file
    file_path = await storage_service.save_file(
        module.course_id,
        module_id,
        lesson.id,
        file_type,
        file_content,
        file.filename,
        file.content_type or "application/octet-stream"
    )
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    return {
        "status": "success",
        "message": "File uploaded successfully",
        "file_path": file_path,
        "filename": file.filename
    }


@router.get("/modules/{module_id}/lessons/{lesson_number}/files")
async def admin_list_lesson_files(
    module_id: str,
    lesson_number: int,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """List all files for a lesson (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number
    from app.crud.module import get_module
    
    # Get lesson
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    files = await storage_service.list_lesson_files(
        module.course_id, module_id, lesson.id
    )
    
    return files


@router.delete("/modules/{module_id}/lessons/{lesson_number}/files/{file_type}/{filename}")
async def admin_delete_file(
    module_id: str,
    lesson_number: int,
    file_type: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete a file from lesson (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number
    from app.crud.module import get_module
    
    # Get lesson
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    success = await storage_service.delete_file(
        module.course_id, module_id, lesson.id, file_type, filename
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return {
        "status": "success",
        "message": "File deleted successfully"
    }


@router.post("/modules/{module_id}/lessons/{lesson_number}/content")
async def admin_save_lesson_content(
    module_id: str,
    lesson_number: int,
    content: str = Form(...),
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Save lesson content (admin only)"""
    from app.crud.lesson import get_lesson_by_module_and_number
    from app.crud.module import get_module
    
    # Get lesson
    lesson = await get_lesson_by_module_and_number(db, module_id, lesson_number)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    success = await storage_service.save_lesson_content(
        module.course_id, module_id, lesson.id, content
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lesson content"
        )
    return {"status": "success", "message": "Lesson content saved"}


# Test Management
@router.get("/modules/{module_id}/test")
async def admin_get_test(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get test questions and settings for editing (admin only)"""
    from app.crud.module import get_module
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Get test questions
    questions = await storage_service.get_test_questions(module.course_id, module_id)
    
    # Get test settings
    settings = await storage_service.get_test_settings(module.course_id, module_id)
    
    # If test doesn't exist, return empty structure
    if not questions:
        questions = {
            "module_id": module_id,
            "questions": []
        }
    
    if not settings:
        settings = {
            "module_id": module_id,
            "passing_threshold": 0.7,
            "time_limit_minutes": 30,
            "max_attempts": 3,
            "shuffle_questions": True,
            "show_results_immediately": False,
            "allow_review": True
        }
    
    return {
        "questions": questions,
        "settings": settings
    }


@router.post("/modules/{module_id}/test/questions")
async def admin_save_test_questions(
    module_id: str,
    test_data: dict,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Save test questions (admin only)"""
    from app.crud.module import get_module
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    success = await storage_service.save_test_questions(module.course_id, module_id, test_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save test questions"
        )
    return {"status": "success", "message": "Test questions saved successfully"}


@router.put("/modules/{module_id}/test/settings")
async def admin_update_test_settings(
    module_id: str,
    settings_data: dict,
    db: AsyncSession = Depends(get_db),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Update test settings (admin only)"""
    from app.crud.module import get_module
    
    # Get module to get course_id
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    success = await storage_service.save_test_settings(module.course_id, module_id, settings_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save test settings"
        )
    return {"status": "success", "message": "Test settings saved successfully"}

