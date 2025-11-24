from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(String(100), primary_key=True)
    module_id = Column(String(50), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    lesson_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")

