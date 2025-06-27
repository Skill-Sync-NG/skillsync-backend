from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.analytics import Analytics
from app.models.match import Match

router = APIRouter()


@router.get("/user-stats")
def get_user_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user analytics and improvement tracking"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Activity stats
    activities = db.query(
        Analytics.event_type,
        func.count(Analytics.id).label("count")
    ).filter(
        Analytics.user_id == current_user.id,
        Analytics.created_at >= start_date
    ).group_by(Analytics.event_type).all()
    
    activity_stats = {activity.event_type: activity.count for activity in activities}
    
    # Match score improvement over time
    matches = db.query(Match).filter(
        Match.user_id == current_user.id,
        Match.created_at >= start_date
    ).order_by(Match.created_at).all()
    
    improvement_trend = []
    if matches:
        # Group matches by week
        weekly_scores = {}
        for match in matches:
            week_key = match.created_at.strftime("%Y-W%U")
            if week_key not in weekly_scores:
                weekly_scores[week_key] = []
            weekly_scores[week_key].append(match.match_score)
        
        # Calculate average score per week
        for week, scores in weekly_scores.items():
            improvement_trend.append({
                "week": week,
                "avg_score": round(sum(scores) / len(scores), 2),
                "match_count": len(scores)
            })
    
    # Best and recent matches
    best_matches = db.query(Match).filter(
        Match.user_id == current_user.id
    ).order_by(desc(Match.match_score)).limit(5).all()
    
    recent_matches = db.query(Match).filter(
        Match.user_id == current_user.id
    ).order_by(desc(Match.created_at)).limit(5).all()
    
    return {
        "period_days": days,
        "activity_stats": activity_stats,
        "improvement_trend": improvement_trend,
        "total_matches": len(matches),
        "avg_match_score": round(sum(m.match_score for m in matches) / len(matches), 2) if matches else 0,
        "best_matches": [
            {
                "match_id": m.id,
                "score": m.match_score,
                "created_at": m.created_at
            } for m in best_matches
        ],
        "recent_matches": [
            {
                "match_id": m.id,
                "score": m.match_score,
                "created_at": m.created_at
            } for m in recent_matches
        ]
    }


@router.get("/skill-gaps")
def get_skill_gap_analysis(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get skill gap analysis across all matches"""
    from app.models.match import SkillGap
    
    # Get all skill gaps for user
    skill_gaps = db.query(
        SkillGap.missing_skill,
        SkillGap.importance,
        func.count(SkillGap.id).label("frequency")
    ).join(Match).filter(
        Match.user_id == current_user.id
    ).group_by(
        SkillGap.missing_skill,
        SkillGap.importance
    ).order_by(desc(func.count(SkillGap.id))).all()
    
    # Group by importance
    skill_analysis = {
        "required": [],
        "preferred": [],
        "other": []
    }
    
    for gap in skill_gaps:
        category = gap.importance if gap.importance in ["required", "preferred"] else "other"
        skill_analysis[category].append({
            "skill": gap.missing_skill,
            "frequency": gap.frequency
        })
    
    # Overall skill recommendations
    top_skills = [gap.missing_skill for gap in skill_gaps[:10]]
    
    return {
        "skill_gaps_by_importance": skill_analysis,
        "top_missing_skills": top_skills,
        "total_unique_gaps": len(skill_gaps)
    }


@router.get("/improvement-suggestions")
def get_improvement_suggestions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized improvement suggestions"""
    # Get recent matches with low scores
    low_score_matches = db.query(Match).filter(
        Match.user_id == current_user.id,
        Match.match_score < 70
    ).order_by(desc(Match.created_at)).limit(10).all()
    
    # Analyze common issues
    common_suggestions = {}
    for match in low_score_matches:
        if match.resume_suggestions:
            for suggestion in match.resume_suggestions:
                if isinstance(suggestion, dict):
                    section = suggestion.get("section", "general")
                    if section not in common_suggestions:
                        common_suggestions[section] = []
                    common_suggestions[section].append(suggestion.get("suggestion", ""))
    
    # Get skill gap patterns
    from app.models.match import SkillGap
    frequent_gaps = db.query(
        SkillGap.missing_skill,
        func.count(SkillGap.id).label("count")
    ).join(Match).filter(
        Match.user_id == current_user.id
    ).group_by(SkillGap.missing_skill).order_by(
        desc(func.count(SkillGap.id))
    ).limit(5).all()
    
    return {
        "priority_improvements": [
            {
                "area": "Skills",
                "suggestion": f"Focus on learning {gap.missing_skill}",
                "frequency": gap.count,
                "impact": "high" if gap.count >= 3 else "medium"
            } for gap in frequent_gaps
        ],
        "resume_improvements": common_suggestions,
        "overall_recommendation": "Focus on the most frequently missing skills to improve your match scores."
    }


@router.post("/track-event")
def track_analytics_event(
    event_type: str,
    event_data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Track custom analytics event"""
    analytics = Analytics(
        user_id=current_user.id,
        event_type=event_type,
        event_data=event_data or {}
    )
    
    db.add(analytics)
    db.commit()
    
    return {"message": "Event tracked successfully"}