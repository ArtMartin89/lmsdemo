from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ModuleBase(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    total_lessons: int
    order_index: int


class ModuleResponse(ModuleBase):
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


