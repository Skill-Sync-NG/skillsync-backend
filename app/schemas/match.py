from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class SkillGapBase(BaseModel):
    missing_skill: str
    importance: Optional[str] = None
    suggestion: Optional[str] = None


class SkillGapResponse(SkillGapBase):
    id: int
    match_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SkillGap(SkillGapResponse):
    pass


class MatchBase(BaseModel):
    match_score: float
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    overall_feedback: Optional[str] = None
    resume_suggestions: Optional[List[Dict[str, Any]]] = None
    cover_letter: Optional[str] = None


class MatchResponse(MatchBase):
    id: int
    user_id: int
    resume_id: int
    job_id: int
    skill_gaps: Optional[List[SkillGapResponse]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Match(MatchResponse):
    pass


class MatchRequest(BaseModel):
    resume_id: int
    job_id: int