from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0-100 percentage
    skill_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    education_match_score = Column(Float, nullable=True)
    overall_feedback = Column(Text, nullable=True)
    resume_suggestions = Column(JSON, nullable=True)  # AI suggestions for resume improvement
    cover_letter = Column(Text, nullable=True)  # Generated cover letter
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")
    skill_gaps = relationship("SkillGap", back_populates="match")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    missing_skill = Column(String, nullable=False)
    importance = Column(String, nullable=True)  # required, preferred, nice-to-have
    suggestion = Column(Text, nullable=True)  # How to acquire this skill
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    match = relationship("Match", back_populates="skill_gaps")