from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeUpdate
from app.services.file_service import FileService
from app.services.resume_parser import ResumeParser
from app.services.ai_service import AIService

router = APIRouter()
file_service = FileService()
resume_parser = ResumeParser()
ai_service = AIService()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    title: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and parse resume file"""
    # Save file
    file_path, original_filename = await file_service.save_file(file, current_user.id)
    
    # Extract text from file
    extracted_text = resume_parser.extract_text(file_path)
    if not extracted_text:
        # Clean up file if parsing failed
        file_service.delete_file(file_path)
        raise HTTPException(
            status_code=400,
            detail="Failed to extract text from file"
        )
    
    # Analyze resume with AI
    parsed_data = await ai_service.analyze_resume(extracted_text)
    
    # Create resume record
    resume = Resume(
        user_id=current_user.id,
        title=title,
        file_path=file_path,
        original_filename=original_filename,
        extracted_text=extracted_text,
        parsed_data=parsed_data,
        skills=parsed_data.get("skills", []),
        experience_years=parsed_data.get("experience_years"),
        education_level=parsed_data.get("education_level")
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    return resume


@router.get("/", response_model=List[ResumeResponse])
def get_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for current user"""
    return db.query(Resume).filter(Resume.user_id == current_user.id).all()


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_update: ResumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    for field, value in resume_update.dict(exclude_unset=True).items():
        setattr(resume, field, value)
    
    db.commit()
    db.refresh(resume)
    
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    if resume.file_path:
        file_service.delete_file(resume.file_path)
    
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}