# Job Application System

AI-powered automated job application system that helps job seekers streamline their application process.

## Features

- 🔍 **Job Fetching**: Automatically fetch jobs from multiple job boards
- 📄 **Resume Generation**: Dynamic LaTeX-based resume generation
- ✍️ **Cover Letters**: AI-powered personalized cover letter creation
- 🎯 **Smart Matching**: ML-based project-to-job matching
- 📊 **Dashboard**: Track applications and monitor success rates

## Quick Start

### Prerequisites

- Python 3.9+
- **Database**: Supabase (recommended) or PostgreSQL 12+
- Redis (optional, for caching and task queues)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-application-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL configuration
   ```

5. **Set up Supabase database**
   ```bash
   # See SUPABASE_SETUP.md for detailed Supabase setup instructions
   # Create database tables:
   python setup_db.py
   
   # IMPORTANT: Set up security (Row-Level Security)
   # See SUPABASE_SECURITY.md for security setup
   ```

6. **Run the application**
   ```bash
   python start_server.py
   ```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Basic system information
- `GET /health` - Health check
- `GET /api/v1/health/detailed` - Detailed health check

### Jobs (Coming Soon)
- `GET /api/v1/jobs` - List jobs with filtering
- `POST /api/v1/jobs/fetch` - Fetch new jobs from external APIs
- `GET /api/v1/jobs/{job_id}` - Get job details

### Projects (Coming Soon)
- `GET /api/v1/projects` - List user projects
- `POST /api/v1/projects` - Create new project
- `PUT /api/v1/projects/{project_id}` - Update project

### Resumes (Coming Soon)
- `POST /api/v1/resumes/generate` - Generate custom resume
- `GET /api/v1/resumes/{resume_id}/download` - Download resume PDF

### Cover Letters (Coming Soon)
- `POST /api/v1/cover-letters/{job_id}` - Generate cover letter
- `GET /api/v1/cover-letters/{cover_letter_id}/download` - Download cover letter

## Development

### Project Structure

```
app/
├── api/v1/           # API endpoints
│   └── endpoints/    # Individual endpoint modules
├── core/             # Core configuration and utilities
├── database/         # Database connection and utilities
├── models/           # SQLAlchemy database models
├── schemas/          # Pydantic validation schemas
├── services/         # Business logic (future)
└── main.py           # Application entry point

alembic/              # Database migrations
├── versions/         # Migration files
└── env.py           # Alembic configuration

logs/                 # Application logs
uploads/              # File storage
├── resumes/         # Generated resume PDFs
└── cover_letters/   # Generated cover letters

.kiro/specs/         # Project specifications and tasks
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

## Configuration

Key environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key for cover letter generation
- `GROQ_API_KEY` - Groq API key (alternative to OpenAI)
- `SECRET_KEY` - Application secret key

## Database Schema

The system uses PostgreSQL with the following tables:

- **users**: User profiles and authentication
- **projects**: User projects with technology tags
- **jobs**: Job listings from external APIs
- **applications**: Application tracking and status

## Next Steps

✅ **Task 1.1**: FastAPI skeleton with logging and API contracts  
✅ **Task 1.2**: PostgreSQL database with core schema  

Upcoming tasks:
1. Implement job fetching from RemoteOK API (Task 2.1)
2. Build resume generation system (Task 3.1)
3. Add AI cover letter generation (Task 4.1)
4. Implement ML-based project matching (Task 5.1)

## License

MIT License