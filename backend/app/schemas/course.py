from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.schemas.module import ModuleResponse


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0


class CourseCreate(CourseBase):
    is_active: bool = True


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourseWithModules(CourseResponse):
    modules: List[ModuleResponse] = []

