from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_recruiter
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobResponse, JobCreate, JobUpdate
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    # Analyze job description with AI
    job_analysis = await ai_service.analyze_job_description(job.description)
    
    # Create job record
    db_job = Job(
        recruiter_id=current_user.id,
        title=job.title,
        company=job.company,
        description=job.description,
        requirements=job.requirements,
        location=job.location,
        job_type=job.job_type,
        salary_range=job.salary_range,
        required_skills=job_analysis.get("required_skills", job.required_skills),
        preferred_skills=job_analysis.get("preferred_skills", job.preferred_skills),
        experience_level=job_analysis.get("experience_level", job.experience_level),
        education_requirement=job_analysis.get("education_requirement", job.education_requirement)
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.get("/", response_model=List[JobResponse])
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active job postings with filtering"""
    query = db.query(Job).filter(Job.is_active)
    
    if search:
        query = query.filter(
            Job.title.contains(search) |
            Job.description.contains(search) |
            Job.company.contains(search)
        )
    
    if location:
        query = query.filter(Job.location.contains(location))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    return query.offset(skip).limit(limit).all()


@router.get("/my-jobs", response_model=List[JobResponse])
def get_my_jobs(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get jobs created by current recruiter"""
    return db.query(Job).filter(Job.recruiter_id == current_user.id).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get specific job"""
    job = db.query(Job).filter(Job.id == job_id, Job.is_active).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Update job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Delete job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}