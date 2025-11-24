from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    progress_id = Column(UUID(as_uuid=True), ForeignKey("user_progress.id"))
    module_id = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False)
    answers = Column(JSON, nullable=False)
    detailed_results = Column(JSON, nullable=False)
    attempt_number = Column(Integer, default=1)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="test_results")


