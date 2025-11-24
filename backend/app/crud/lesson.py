from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.lesson import Lesson


async def get_lesson(db: AsyncSession, lesson_id: str) -> Optional[Lesson]:
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    return result.scalar_one_or_none()


async def get_lesson_by_module_and_number(
    db: AsyncSession, 
    module_id: str, 
    lesson_number: int
) -> Optional[Lesson]:
    result = await db.execute(
        select(Lesson).where(
            Lesson.module_id == module_id,
            Lesson.lesson_number == lesson_number
        )
    )
    return result.scalar_one_or_none()


async def get_all_lessons(
    db: AsyncSession, 
    module_id: Optional[str] = None,
    include_inactive: bool = False
) -> List[Lesson]:
    query = select(Lesson)
    if module_id:
        query = query.where(Lesson.module_id == module_id)
    query = query.order_by(Lesson.order_index)
    if not include_inactive:
        query = query.where(Lesson.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_lesson(db: AsyncSession, lesson_data: dict) -> Lesson:
    lesson = Lesson(**lesson_data)
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def update_lesson(
    db: AsyncSession, 
    lesson_id: str, 
    lesson_data: dict
) -> Optional[Lesson]:
    lesson = await get_lesson(db, lesson_id)
    if not lesson:
        return None
    
    for key, value in lesson_data.items():
        setattr(lesson, key, value)
    
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def delete_lesson(db: AsyncSession, lesson_id: str) -> bool:
    lesson = await get_lesson(db, lesson_id)
    if not lesson:
        return False
    
    await db.delete(lesson)
    await db.commit()
    return True

