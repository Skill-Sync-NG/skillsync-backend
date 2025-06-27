from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AnalyticsBase(BaseModel):
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    improvement_score: Optional[float] = None
    session_id: Optional[str] = None


class AnalyticsCreate(AnalyticsBase):
    pass


class AnalyticsResponse(AnalyticsBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Analytics(AnalyticsResponse):
    pass