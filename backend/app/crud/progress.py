from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from app.models.progress import UserProgress, ProgressStatus


async def get_user_progress(
    db: AsyncSession, 
    user_id: UUID, 
    module_id: str
) -> Optional[UserProgress]:
    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == user_id)
        .where(UserProgress.module_id == module_id)
    )
    return result.scalar_one_or_none()


async def get_all_user_progress(
    db: AsyncSession, 
    user_id: UUID
) -> List[UserProgress]:
    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == user_id)
        .order_by(UserProgress.started_at)
    )
    return list(result.scalars().all())


async def create_user_progress(
    db: AsyncSession,
    user_id: UUID,
    module_id: str,
    total_lessons: int
) -> UserProgress:
    progress = UserProgress(
        user_id=user_id,
        module_id=module_id,
        total_lessons=total_lessons,
        status=ProgressStatus.IN_PROGRESS,
        current_lesson=0
    )
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress


async def update_current_lesson(
    db: AsyncSession,
    progress_id: UUID,
    lesson_number: int
) -> UserProgress:
    result = await db.execute(
        select(UserProgress).where(UserProgress.id == progress_id)
    )
    progress = result.scalar_one()
    progress.current_lesson = lesson_number
    await db.commit()
    await db.refresh(progress)
    return progress


async def update_status(
    db: AsyncSession,
    progress_id: UUID,
    status: ProgressStatus
) -> UserProgress:
    result = await db.execute(
        select(UserProgress).where(UserProgress.id == progress_id)
    )
    progress = result.scalar_one()
    progress.status = status
    await db.commit()
    await db.refresh(progress)
    return progress


