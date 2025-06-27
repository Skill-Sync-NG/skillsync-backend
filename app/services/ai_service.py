from openai import OpenAI
from typing import Dict, List, Any
from app.core.config import settings
import json


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured data from resume text using AI"""
        prompt = f"""
        Analyze the following resume text and extract structured information:
        
        {resume_text}
        
        Please return a JSON object with the following structure:
        {{
            "skills": ["skill1", "skill2", ...],
            "experience_years": number,
            "education_level": "string",
            "work_experience": [
                {{
                    "company": "string",
                    "position": "string",
                    "duration": "string",
                    "description": "string"
                }}
            ],
            "education": [
                {{
                    "institution": "string",
                    "degree": "string",
                    "field": "string",
                    "year": "string"
                }}
            ],
            "contact_info": {{
                "email": "string",
                "phone": "string",
                "location": "string"
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            return {}

    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Extract structured data from job description using AI"""
        prompt = f"""
        Analyze the following job description and extract structured information:
        
        {job_description}
        
        Please return a JSON object with the following structure:
        {{
            "required_skills": ["skill1", "skill2", ...],
            "preferred_skills": ["skill1", "skill2", ...],
            "experience_level": "entry/mid/senior",
            "education_requirement": "string",
            "key_responsibilities": ["resp1", "resp2", ...],
            "company_benefits": ["benefit1", "benefit2", ...],
            "job_type": "full-time/part-time/contract",
            "remote_option": "yes/no/hybrid"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert job description analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            print(f"Error analyzing job description: {e}")
            return {}

    async def calculate_match_score(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate match score between resume and job description"""
        prompt = f"""
        Calculate a match score between this resume and job description:
        
        RESUME DATA:
        {json.dumps(resume_data, indent=2)}
        
        JOB DATA:
        {json.dumps(job_data, indent=2)}
        
        Please return a JSON object with the following structure:
        {{
            "overall_score": number (0-100),
            "skill_match_score": number (0-100),
            "experience_match_score": number (0-100),
            "education_match_score": number (0-100),
            "missing_skills": [
                {{
                    "skill": "string",
                    "importance": "required/preferred",
                    "suggestion": "string"
                }}
            ],
            "strengths": ["strength1", "strength2", ...],
            "weaknesses": ["weakness1", "weakness2", ...],
            "overall_feedback": "detailed feedback string"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst. Provide accurate match scoring."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return {"overall_score": 0, "skill_match_score": 0, "experience_match_score": 0, "education_match_score": 0}

    async def generate_resume_suggestions(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any], match_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate suggestions for improving resume based on job requirements"""
        prompt = f"""
        Based on this resume and job analysis, provide specific suggestions for improving the resume:
        
        RESUME: {json.dumps(resume_data, indent=2)}
        JOB: {json.dumps(job_data, indent=2)}
        MATCH ANALYSIS: {json.dumps(match_analysis, indent=2)}
        
        Please return a JSON array of suggestions with this structure:
        [
            {{
                "section": "skills/experience/education/summary",
                "suggestion": "specific improvement suggestion",
                "priority": "high/medium/low",
                "impact": "explanation of how this helps"
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume coach. Provide actionable suggestions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            print(f"Error generating resume suggestions: {e}")
            return []

    async def generate_cover_letter(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any], user_name: str
    ) -> str:
        """Generate a personalized cover letter"""
        prompt = f"""
        Generate a professional cover letter for {user_name} based on their resume and the job description:
        
        RESUME: {json.dumps(resume_data, indent=2)}
        JOB: {json.dumps(job_data, indent=2)}
        
        The cover letter should:
        - Be professional and engaging
        - Highlight relevant skills and experiences
        - Show enthusiasm for the role
        - Be 3-4 paragraphs long
        - Include a proper greeting and closing
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer. Write compelling, professional cover letters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return "Unable to generate cover letter at this time."