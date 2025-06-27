from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # resume_upload, job_match, cover_letter_generate
    event_data = Column(JSON, nullable=True)  # Additional event details
    improvement_score = Column(Float, nullable=True)  # Track improvement over time
    session_id = Column(String, nullable=True)  # Track user sessions
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="analytics")