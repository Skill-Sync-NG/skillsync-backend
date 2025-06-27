import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings


class FileService:
    def __init__(self):
        # Use current working directory if /app doesn't exist
        base_path = Path("/app") if Path("/app").exists() else Path.cwd()
        self.upload_dir = base_path / "storage" / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Check file extension
        if file.filename:
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in settings.ALLOWED_FILE_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
                )
        
        return True

    async def save_file(self, file: UploadFile, user_id: int) -> tuple[str, str]:
        """Save uploaded file and return file path and filename"""
        self.validate_file(file)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower() if file.filename else ""
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            return str(file_path), file.filename or unique_filename
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )

    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False