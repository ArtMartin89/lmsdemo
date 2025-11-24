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
    return courses


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
    admin_user: User = Depends(get_current_admin_user)
):
    """Create a new course (admin only)"""
    course = await create_course(db, course_data.dict())
    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def admin_update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """Update course (admin only)"""
    course = await update_course(db, course_id, course_data.dict(exclude_unset=True))
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


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


# Lesson Content Management
@router.get("/modules/{module_id}/lessons/{lesson_number}")
async def admin_get_lesson(
    module_id: str,
    lesson_number: int,
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get lesson content for editing (admin only)"""
    content = await storage_service.get_lesson_content(module_id, lesson_number)
    
    # If lesson doesn't exist, return empty content
    if not content:
        content = {
            "module_id": module_id,
            "lesson_number": lesson_number,
            "content": "",
            "content_type": "markdown"
        }
    
    # Get list of files
    files = await storage_service.list_lesson_files(module_id, lesson_number)
    content["files"] = files
    
    return content


@router.post("/modules/{module_id}/lessons/{lesson_number}")
async def admin_save_lesson(
    module_id: str,
    lesson_number: int,
    content: str = Form(...),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Save lesson content (admin only)"""
    success = await storage_service.save_lesson_content(
        module_id, lesson_number, content
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lesson content"
        )
    return {"status": "success", "message": "Lesson content saved"}


@router.post("/modules/{module_id}/lessons/{lesson_number}/files")
async def admin_upload_file(
    module_id: str,
    lesson_number: int,
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Upload a file for a lesson (admin only)"""
    # Read file content
    file_content = await file.read()
    
    # Save file
    file_path = await storage_service.save_file(
        module_id,
        lesson_number,
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


@router.get("/files/{module_id}/{lesson_number}/{filename}")
async def admin_get_file(
    module_id: str,
    lesson_number: int,
    filename: str,
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get file content (admin only)"""
    file_content = await storage_service.get_file(module_id, lesson_number, filename)
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine content type from filename
    content_type = "application/octet-stream"
    if filename.endswith((".mp3", ".wav", ".ogg")):
        content_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    elif filename.endswith((".mp4", ".webm")):
        content_type = "video/mp4" if filename.endswith(".mp4") else "video/webm"
    elif filename.endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif filename.endswith(".png"):
        content_type = "image/png"
    elif filename.endswith(".gif"):
        content_type = "image/gif"
    
    return Response(
        content=file_content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )


@router.delete("/files/{module_id}/{lesson_number}/{filename}")
async def admin_delete_file(
    module_id: str,
    lesson_number: int,
    filename: str,
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete a file (admin only)"""
    success = await storage_service.delete_file(module_id, lesson_number, filename)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return {
        "status": "success",
        "message": "File deleted successfully"
    }


# Test Management
@router.get("/modules/{module_id}/test")
async def admin_get_test(
    module_id: str,
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Get test questions for editing (admin only)"""
    test_data = await storage_service.get_test_questions(module_id)
    
    # If test doesn't exist, return empty structure
    if not test_data:
        test_data = {
            "module_id": module_id,
            "passing_threshold": 0.7,
            "time_limit_minutes": 30,
            "questions": []
        }
    
    return test_data


@router.post("/modules/{module_id}/test")
async def admin_save_test(
    module_id: str,
    test_data: dict,
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: User = Depends(get_current_admin_user)
):
    """Save test questions (admin only)"""
    success = await storage_service.save_test_questions(module_id, test_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save test"
        )
    return {"status": "success", "message": "Test saved successfully"}

