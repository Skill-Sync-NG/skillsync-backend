from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)  # full-time, part-time, contract
    salary_range = Column(String, nullable=True)
    required_skills = Column(JSON, nullable=True)  # Extracted required skills
    preferred_skills = Column(JSON, nullable=True)  # Extracted preferred skills
    experience_level = Column(String, nullable=True)  # entry, mid, senior
    education_requirement = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    recruiter = relationship("User", back_populates="jobs")
    matches = relationship("Match", back_populates="job")