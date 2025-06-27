from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.deps import get_db, get_current_recruiter
from app.models.user import User
from app.models.job import Job
from app.models.match import Match
from app.models.resume import Resume

router = APIRouter()


@router.get("/candidates/{job_id}")
def get_candidates_for_job(
    job_id: int,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get ranked candidates for a specific job"""
    # Verify job belongs to recruiter
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get matches for this job, ordered by score
    matches = db.query(Match).join(Resume).join(User).filter(
        Match.job_id == job_id,
        Match.match_score >= min_score
    ).order_by(desc(Match.match_score)).limit(limit).all()
    
    # Format response with candidate info
    candidates = []
    for match in matches:
        resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
        user = db.query(User).filter(User.id == match.user_id).first()
        
        candidates.append({
            "match_id": match.id,
            "candidate_name": user.full_name,
            "candidate_email": user.email,
            "resume_title": resume.title,
            "match_score": match.match_score,
            "skill_match_score": match.skill_match_score,
            "experience_match_score": match.experience_match_score,
            "education_match_score": match.education_match_score,
            "skills": resume.skills,
            "experience_years": resume.experience_years,
            "education_level": resume.education_level,
            "created_at": match.created_at
        })
    
    return {
        "job_title": job.title,
        "job_company": job.company,
        "total_candidates": len(candidates),
        "candidates": candidates
    }


@router.get("/jobs/stats")
def get_job_stats(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get statistics for recruiter's jobs"""
    # Get job stats
    job_stats = db.query(
        Job.id,
        Job.title,
        Job.company,
        Job.created_at,
        func.count(Match.id).label("total_matches"),
        func.avg(Match.match_score).label("avg_match_score"),
        func.max(Match.match_score).label("best_match_score")
    ).outerjoin(Match).filter(
        Job.recruiter_id == current_user.id
    ).group_by(Job.id).all()
    
    return [
        {
            "job_id": stat.id,
            "job_title": stat.title,
            "company": stat.company,
            "created_at": stat.created_at,
            "total_matches": stat.total_matches or 0,
            "avg_match_score": round(stat.avg_match_score or 0, 2),
            "best_match_score": stat.best_match_score or 0
        }
        for stat in job_stats
    ]


@router.get("/overview")
def get_dashboard_overview(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get overview statistics for recruiter dashboard"""
    # Total jobs
    total_jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).count()
    
    # Active jobs
    active_jobs = db.query(Job).filter(
        Job.recruiter_id == current_user.id,
        Job.is_active
    ).count()
    
    # Total matches across all jobs
    total_matches = db.query(Match).join(Job).filter(
        Job.recruiter_id == current_user.id
    ).count()
    
    # High-quality matches (score >= 80)
    high_quality_matches = db.query(Match).join(Job).filter(
        Job.recruiter_id == current_user.id,
        Match.match_score >= 80
    ).count()
    
    # Recent matches (last 7 days)
    from datetime import datetime, timedelta
    recent_matches = db.query(Match).join(Job).filter(
        Job.recruiter_id == current_user.id,
        Match.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Top performing job
    top_job = db.query(
        Job.title,
        func.count(Match.id).label("match_count"),
        func.avg(Match.match_score).label("avg_score")
    ).outerjoin(Match).filter(
        Job.recruiter_id == current_user.id
    ).group_by(Job.id).order_by(
        desc(func.count(Match.id))
    ).first()
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_matches": total_matches,
        "high_quality_matches": high_quality_matches,
        "recent_matches": recent_matches,
        "top_performing_job": {
            "title": top_job.title if top_job else None,
            "match_count": top_job.match_count if top_job else 0,
            "avg_score": round(top_job.avg_score or 0, 2) if top_job else 0
        }
    }