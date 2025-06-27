from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ResumeBase(BaseModel):
    title: str
    extracted_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    extracted_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Resume(ResumeResponse):
    pass