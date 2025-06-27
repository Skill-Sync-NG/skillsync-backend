![CI](https://github.com/Skill-Sync-NG/skillsync-backend/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/github/v/release/Skill-Sync-NG/skillsync-backend)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)

# SkillSync - AI Resume & Job Match Hub

SkillSync is an AI-powered backend API that helps job seekers match their resumes with job descriptions, provides skill gap analysis, resume improvement suggestions, and generates personalized cover letters. It also includes a recruiter dashboard for candidate ranking and management.

## Features

### Core Features
- **Resume Upload & Parsing**: Upload PDF, DOCX, or TXT resume files with AI-powered text extraction
- **Job Description Analysis**: AI analysis of job postings to extract required skills and requirements
- **AI Matching & Scoring**: Intelligent matching between resumes and jobs with detailed scoring
- **Skill Gap Analysis**: Identify missing skills and get suggestions for improvement
- **Resume Suggestions**: AI-powered recommendations to improve resume content
- **Cover Letter Generation**: Personalized cover letter creation based on resume and job match
- **Recruiter Dashboard**: Advanced candidate ranking and job management for recruiters
- **Analytics & Tracking**: User improvement tracking and engagement analytics

### Technical Features
- **FastAPI Framework**: Modern, fast web framework for building APIs
- **SQLite Database**: Lightweight, serverless database with SQLAlchemy ORM
- **JWT Authentication**: Secure user authentication with role-based access control
- **OpenAI Integration**: Powered by GPT models for intelligent text analysis
- **File Upload Support**: Secure file handling with validation
- **CORS Enabled**: Cross-origin resource sharing for frontend integration
- **Comprehensive API Documentation**: Auto-generated OpenAPI/Swagger docs

## Tech Stack

- **Backend**: Python 3.9+ with FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: OpenAI GPT-3.5/4 for text analysis and generation
- **Authentication**: JWT tokens with bcrypt password hashing
- **File Processing**: PyPDF2, python-docx for document parsing
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skillsync-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-super-secret-key-change-in-production
   OPENAI_API_KEY=your-openai-api-key
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Production Deployment

For production deployment, ensure you set the following environment variables:

- `SECRET_KEY`: A strong secret key for JWT token signing
- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

### Resume Management
- `POST /api/v1/resumes/upload` - Upload and parse resume
- `GET /api/v1/resumes/` - Get user's resumes
- `GET /api/v1/resumes/{resume_id}` - Get specific resume
- `PUT /api/v1/resumes/{resume_id}` - Update resume
- `DELETE /api/v1/resumes/{resume_id}` - Delete resume

### Job Management
- `POST /api/v1/jobs/` - Create job posting (recruiters only)
- `GET /api/v1/jobs/` - Get all active jobs with filters
- `GET /api/v1/jobs/my-jobs` - Get recruiter's jobs
- `GET /api/v1/jobs/{job_id}` - Get specific job
- `PUT /api/v1/jobs/{job_id}` - Update job posting
- `DELETE /api/v1/jobs/{job_id}` - Delete job posting

### AI Matching
- `POST /api/v1/matching/analyze` - Analyze resume-job match
- `GET /api/v1/matching/` - Get user's matches
- `GET /api/v1/matching/{match_id}` - Get specific match
- `POST /api/v1/matching/{match_id}/cover-letter` - Generate cover letter

### Recruiter Dashboard
- `GET /api/v1/dashboard/candidates/{job_id}` - Get ranked candidates for job
- `GET /api/v1/dashboard/jobs/stats` - Get job statistics
- `GET /api/v1/dashboard/overview` - Get dashboard overview

### Analytics
- `GET /api/v1/analytics/user-stats` - Get user analytics
- `GET /api/v1/analytics/skill-gaps` - Get skill gap analysis
- `GET /api/v1/analytics/improvement-suggestions` - Get improvement suggestions
- `POST /api/v1/analytics/track-event` - Track custom events

## User Roles

### Applicant (Default)
- Upload and manage resumes
- Search and view job postings
- Get AI-powered job matching and scoring
- Receive skill gap analysis and resume suggestions
- Generate personalized cover letters
- Track improvement analytics

### Recruiter
- All applicant features
- Create and manage job postings
- Access recruiter dashboard
- View ranked candidates for jobs
- Get job performance statistics

### Admin
- All recruiter and applicant features
- System administration capabilities

## Database Schema

The application uses SQLite with the following main tables:
- `users` - User accounts and authentication
- `resumes` - Resume data and metadata
- `jobs` - Job postings and requirements
- `matches` - Resume-job matches with AI scoring
- `skill_gaps` - Identified skill gaps from matches
- `analytics` - User activity and improvement tracking

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality

### Optional Variables (with defaults)
- `SECRET_KEY`: JWT secret key (default: change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `MAX_FILE_SIZE`: Maximum upload file size in bytes (default: 10MB)

## File Storage

The application stores uploaded files in `/app/storage/` with the following structure:
- `/app/storage/db/` - SQLite database file
- `/app/storage/uploads/` - Uploaded resume files

## Development

### Code Style
The project uses Ruff for linting and code formatting:
```bash
ruff check .
ruff format .
```

### Testing
Run tests with pytest:
```bash
pytest
```

### Database Migrations
Create new migrations:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the repository.