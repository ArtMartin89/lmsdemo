from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.crud.course import get_all_courses, get_course
from app.crud.module import get_all_modules
from app.schemas.course import CourseResponse, CourseWithModules

router = APIRouter()


@router.get("", response_model=List[CourseWithModules])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available courses with their modules"""
    courses = await get_all_courses(db, include_inactive=False)
    
    # Get modules for each course
    result = []
    for course in courses:
        modules = await get_all_modules(db, include_inactive=False, course_id=course.id)
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "order_index": course.order_index,
            "is_active": course.is_active,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "modules": modules
        }
        result.append(course_dict)
    
    return result


@router.get("/{course_id}", response_model=CourseWithModules)
async def get_course_details(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get course details with modules"""
    from uuid import UUID
    try:
        course_uuid = UUID(course_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID format"
        )
    
    course = await get_course(db, course_uuid)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get modules for this course
    modules = await get_all_modules(db, include_inactive=False, course_id=course_uuid)
    
    course_dict = {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "order_index": course.order_index,
        "is_active": course.is_active,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
        "modules": modules
    }
    return course_dict

