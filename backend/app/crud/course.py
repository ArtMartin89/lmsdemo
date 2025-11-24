from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.models.course import Course


async def get_course(db: AsyncSession, course_id: UUID) -> Optional[Course]:
    result = await db.execute(select(Course).where(Course.id == course_id))
    return result.scalar_one_or_none()


async def get_all_courses(db: AsyncSession, include_inactive: bool = False) -> List[Course]:
    query = select(Course).order_by(Course.order_index)
    if not include_inactive:
        query = query.where(Course.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_course(db: AsyncSession, course_data: dict) -> Course:
    course = Course(**course_data)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def update_course(db: AsyncSession, course_id: UUID, course_data: dict) -> Optional[Course]:
    course = await get_course(db, course_id)
    if not course:
        return None
    
    for key, value in course_data.items():
        setattr(course, key, value)
    
    await db.commit()
    await db.refresh(course)
    return course


async def delete_course(db: AsyncSession, course_id: UUID) -> bool:
    course = await get_course(db, course_id)
    if not course:
        return False
    
    await db.delete(course)
    await db.commit()
    return True

