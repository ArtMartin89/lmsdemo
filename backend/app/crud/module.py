from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.module import Module


async def get_module(db: AsyncSession, module_id: str) -> Optional[Module]:
    result = await db.execute(select(Module).where(Module.id == module_id))
    return result.scalar_one_or_none()


async def get_all_modules(db: AsyncSession) -> List[Module]:
    result = await db.execute(
        select(Module)
        .where(Module.is_active == True)
        .order_by(Module.order_index)
    )
    return list(result.scalars().all())


