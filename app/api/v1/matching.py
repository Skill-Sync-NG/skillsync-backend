from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.match import Match, SkillGap
from app.schemas.match import MatchResponse, MatchRequest
from app.services.ai_service import AIService
from app.models.analytics import Analytics

router = APIRouter()
ai_service = AIService()


@router.post("/analyze", response_model=MatchResponse)
async def analyze_match(
    match_request: MatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze match between resume and job description"""
    # Verify resume belongs to user
    resume = db.query(Resume).filter(
        Resume.id == match_request.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get job
    job = db.query(Job).filter(
        Job.id == match_request.job_id,
        Job.is_active
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if match already exists
    existing_match = db.query(Match).filter(
        Match.user_id == current_user.id,
        Match.resume_id == match_request.resume_id,
        Match.job_id == match_request.job_id
    ).first()
    
    if existing_match:
        return existing_match
    
    # Prepare data for AI analysis
    resume_data = {
        "skills": resume.skills or [],
        "experience_years": resume.experience_years,
        "education_level": resume.education_level,
        "parsed_data": resume.parsed_data or {}
    }
    
    job_data = {
        "required_skills": job.required_skills or [],
        "preferred_skills": job.preferred_skills or [],
        "experience_level": job.experience_level,
        "education_requirement": job.education_requirement,
        "description": job.description
    }
    
    # Calculate match score using AI
    match_analysis = await ai_service.calculate_match_score(resume_data, job_data)
    
    # Generate resume suggestions
    suggestions = await ai_service.generate_resume_suggestions(
        resume_data, job_data, match_analysis
    )
    
    # Create match record
    match = Match(
        user_id=current_user.id,
        resume_id=match_request.resume_id,
        job_id=match_request.job_id,
        match_score=match_analysis.get("overall_score", 0),
        skill_match_score=match_analysis.get("skill_match_score", 0),
        experience_match_score=match_analysis.get("experience_match_score", 0),
        education_match_score=match_analysis.get("education_match_score", 0),
        overall_feedback=match_analysis.get("overall_feedback", ""),
        resume_suggestions=suggestions
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    # Create skill gap records
    missing_skills = match_analysis.get("missing_skills", [])
    for skill_data in missing_skills:
        skill_gap = SkillGap(
            match_id=match.id,
            missing_skill=skill_data.get("skill", ""),
            importance=skill_data.get("importance", ""),
            suggestion=skill_data.get("suggestion", "")
        )
        db.add(skill_gap)
    
    db.commit()
    
    # Log analytics
    analytics = Analytics(
        user_id=current_user.id,
        event_type="job_match",
        event_data={
            "resume_id": match_request.resume_id,
            "job_id": match_request.job_id,
            "match_score": match.match_score
        },
        improvement_score=match.match_score
    )
    db.add(analytics)
    db.commit()
    
    # Refresh to get skill gaps
    db.refresh(match)
    
    return match


@router.get("/", response_model=List[MatchResponse])
def get_matches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all matches for current user"""
    return db.query(Match).filter(Match.user_id == current_user.id).all()


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific match"""
    match = db.query(Match).filter(
        Match.id == match_id,
        Match.user_id == current_user.id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match


@router.post("/{match_id}/cover-letter")
async def generate_cover_letter(
    match_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate cover letter for specific match"""
    match = db.query(Match).filter(
        Match.id == match_id,
        Match.user_id == current_user.id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get resume and job data
    resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
    job = db.query(Job).filter(Job.id == match.job_id).first()
    
    resume_data = {
        "skills": resume.skills or [],
        "experience_years": resume.experience_years,
        "education_level": resume.education_level,
        "parsed_data": resume.parsed_data or {}
    }
    
    job_data = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "required_skills": job.required_skills or [],
        "preferred_skills": job.preferred_skills or []
    }
    
    # Generate cover letter
    cover_letter = await ai_service.generate_cover_letter(
        resume_data, job_data, current_user.full_name
    )
    
    # Update match with cover letter
    match.cover_letter = cover_letter
    db.commit()
    
    # Log analytics
    analytics = Analytics(
        user_id=current_user.id,
        event_type="cover_letter_generate",
        event_data={
            "match_id": match_id,
            "job_id": match.job_id
        }
    )
    db.add(analytics)
    db.commit()
    
    return {"cover_letter": cover_letter}