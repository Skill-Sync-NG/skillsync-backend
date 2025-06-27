from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    extracted_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Structured resume data
    skills = Column(JSON, nullable=True)  # Extracted skills
    experience_years = Column(Integer, nullable=True)
    education_level = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume")