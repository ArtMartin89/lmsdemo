from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from datetime import datetime

from app.db.base import Base


class Module(Base):
    __tablename__ = "modules"
    
    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    total_lessons = Column(Integer, nullable=False)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


