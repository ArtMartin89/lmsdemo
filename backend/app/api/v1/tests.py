from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.progress import ProgressStatus
from app.models.test import TestResult
from app.services.content_service import ContentService
from app.services.test_service import TestGradingService
from app.services.progress_service import ProgressService
from app.schemas.test import TestSubmission, TestResultResponse
from app.dependencies import (
    get_content_service,
    get_grading_service,
    get_progress_service
)

router = APIRouter()


@router.get("/modules/{module_id}/test")
async def get_test_questions(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get test questions for a module"""
    # Get user progress
    progress = await progress_service.get_user_progress(
        current_user.id, module_id
    )
    
    if not progress or progress.status != ProgressStatus.TESTING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test not available. Complete all lessons first."
        )
    
    test_questions = await content_service.get_test_questions(module_id, db)
    
    if not test_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test questions not found"
        )
    
    return test_questions


@router.post("/modules/{module_id}/test", response_model=TestResultResponse)
async def submit_test(
    module_id: str,
    submission: TestSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
    grading_service: TestGradingService = Depends(get_grading_service),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Submit test answers and get results"""
    # Get user progress
    progress = await progress_service.get_user_progress(
        current_user.id, module_id
    )
    
    if not progress or progress.status != ProgressStatus.TESTING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test not available. Complete all lessons first."
        )
    
    # Get test questions (which contain correct answers)
    test_questions_data = await content_service.get_test_questions(module_id, db)
    
    if not test_questions_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Test questions not found"
        )
    
    # Format answers for grading
    user_answers = [{"question_id": ans.question_id, "answer": ans.answer} for ans in submission.answers]
    
    # Extract questions with correct answers
    questions = test_questions_data.get("questions", [])
    
    # Grade test
    result = grading_service.grade_test(
        user_answers,
        questions
    )
    
    # Calculate attempt number
    attempt_number = len(progress.test_results) + 1
    
    # Save result
    test_result = TestResult(
        progress_id=progress.id,
        module_id=module_id,
        score=result.score,
        max_score=result.max_score,
        percentage=result.percentage,
        passed=result.passed,
        answers=[{"question_id": ans.question_id, "answer": ans.answer} for ans in submission.answers],
        detailed_results=[detail.dict() for detail in result.detailed_results],
        attempt_number=attempt_number
    )
    
    db.add(test_result)
    
    # Update progress status
    if result.passed:
        progress.status = ProgressStatus.COMPLETED
        progress.completed_at = datetime.utcnow()
    else:
        progress.status = ProgressStatus.FAILED
    
    await db.commit()
    await db.refresh(test_result)
    
    # Calculate next module
    next_module_unlocked = None
    if result.passed:
        try:
            module_num = int(module_id.split("_")[1])
            next_module_unlocked = f"Module_{module_num + 1:02d}"
        except:
            pass
    
    return TestResultResponse(
        status="test_completed",
        result_id=test_result.id,
        score=result.score,
        max_score=result.max_score,
        percentage=result.percentage,
        passed=result.passed,
        detailed_results=result.detailed_results,
        attempt_number=attempt_number,
        next_module_unlocked=next_module_unlocked
    )


@router.get("/results/{result_id}")
async def get_test_result(
    result_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get test result by ID"""
    from sqlalchemy import select
    from uuid import UUID
    
    result = await db.execute(
        select(TestResult).where(TestResult.id == UUID(result_id))
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found"
        )
    
    # Verify ownership
    if test_result.progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return test_result


