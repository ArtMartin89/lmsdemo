from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    module_id = Column(String(50), nullable=False)
    current_lesson = Column(Integer, default=0)
    total_lessons = Column(Integer, nullable=False)
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    test_results = relationship("TestResult", back_populates="progress", cascade="all, delete-orphan")


