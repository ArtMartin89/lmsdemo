from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.module import Module


async def get_module(db: AsyncSession, module_id: str) -> Optional[Module]:
    result = await db.execute(select(Module).where(Module.id == module_id))
    return result.scalar_one_or_none()


async def get_all_modules(db: AsyncSession, include_inactive: bool = False) -> List[Module]:
    query = select(Module).order_by(Module.order_index)
    if not include_inactive:
        query = query.where(Module.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_module(db: AsyncSession, module_data: dict) -> Module:
    module = Module(**module_data)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


async def update_module(db: AsyncSession, module_id: str, module_data: dict) -> Optional[Module]:
    module = await get_module(db, module_id)
    if not module:
        return None
    
    for key, value in module_data.items():
        setattr(module, key, value)
    
    await db.commit()
    await db.refresh(module)
    return module


async def delete_module(db: AsyncSession, module_id: str) -> bool:
    module = await get_module(db, module_id)
    if not module:
        return False
    
    await db.delete(module)
    await db.commit()
    return True


