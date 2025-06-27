import PyPDF2
import docx
from typing import Optional
from pathlib import Path


class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return None

    @staticmethod
    def extract_text_from_docx(file_path: str) -> Optional[str]:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return None

    @staticmethod
    def extract_text_from_txt(file_path: str) -> Optional[str]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error extracting TXT text: {e}")
            return None

    @classmethod
    def extract_text(cls, file_path: str) -> Optional[str]:
        """Extract text from file based on extension"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return cls.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return cls.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return cls.extract_text_from_txt(file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return None