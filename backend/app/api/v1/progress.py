from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.crud.progress import get_all_user_progress
from app.schemas.progress import ProgressResponse, OverallProgressResponse
from app.models.test import TestResult
from sqlalchemy import select, func

router = APIRouter()


@router.get("", response_model=OverallProgressResponse)
async def get_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's overall progress"""
    all_progress = await get_all_user_progress(db, current_user.id)
    
    completed_modules = sum(1 for p in all_progress if p.status.value == "completed")
    in_progress_modules = sum(1 for p in all_progress if p.status.value in ["in_progress", "testing"])
    
    # Calculate average grade
    completed_progress_ids = [p.id for p in all_progress if p.status.value == "completed"]
    average_grade = None
    
    if completed_progress_ids:
        result = await db.execute(
            select(func.avg(TestResult.percentage))
            .where(TestResult.progress_id.in_(completed_progress_ids))
            .where(TestResult.passed == True)
        )
        avg = result.scalar()
        if avg:
            average_grade = round(float(avg) / 10, 1)  # Convert to 10-point scale
    
    return OverallProgressResponse(
        total_modules=len(all_progress),
        completed_modules=completed_modules,
        in_progress_modules=in_progress_modules,
        average_grade=average_grade,
        modules=[ProgressResponse(
            module_id=p.module_id,
            current_lesson=p.current_lesson,
            total_lessons=p.total_lessons,
            status=p.status,
            progress_percentage=int((p.current_lesson / p.total_lessons) * 100) if p.total_lessons > 0 else 0,
            started_at=p.started_at,
            updated_at=p.updated_at,
            completed_at=p.completed_at
        ) for p in all_progress]
    )


@router.get("/{module_id}", response_model=ProgressResponse)
async def get_module_progress(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for specific module"""
    from app.crud.progress import get_user_progress
    
    progress = await get_user_progress(db, current_user.id, module_id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this module"
        )
    
    return ProgressResponse(
        module_id=progress.module_id,
        current_lesson=progress.current_lesson,
        total_lessons=progress.total_lessons,
        status=progress.status,
        progress_percentage=int((progress.current_lesson / progress.total_lessons) * 100) if progress.total_lessons > 0 else 0,
        started_at=progress.started_at,
        updated_at=progress.updated_at,
        completed_at=progress.completed_at
    )


