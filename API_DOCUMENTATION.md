# 📚 API Documentation

Complete REST API reference for the Job Application Automation System.

## 🔗 Base URL

```
http://localhost:8000/api/v1
```

## 🔍 Job Management Endpoints

### Get Jobs

```http
GET /jobs
```

**Query Parameters:**

- `keywords` (string, optional): Comma-separated search keywords
- `location` (string, optional): Job location filter
- `company` (string, optional): Company name filter
- `limit` (int, default: 20): Number of jobs to return
- `offset` (int, default: 0): Pagination offset

**Response:**

```json
[
  {
    "id": "uuid",
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "description": "Job description...",
    "location": "San Francisco, CA",
    "salary_range": "$120k - $150k",
    "requirements": ["Python", "FastAPI", "PostgreSQL"],
    "source": "RemoteOK",
    "posted_date": "2024-01-15T10:30:00Z"
  }
]
```

### Fetch New Jobs

```http
POST /jobs/fetch
```

**Request Body:**

```json
{
  "keywords": ["python", "react"],
  "limit_per_source": 10
}
```

**Response:**

```json
{
  "success": true,
  "message": "Fetched 25 jobs, 20 new, 5 updated",
  "results": {
    "total_fetched": 25,
    "new_jobs": 20,
    "updated_jobs": 5,
    "sources": {
      "RemoteOK": {"fetched": 8, "new": 6, "updated": 2, "status": "success"},
      "GitHub": {"fetched": 12, "new": 10, "updated": 2, "status": "success"},
      "Reed": {"fetched": 5, "new": 4, "updated": 1, "status": "success"}
    }
  }
}
```

### Get Job Sources

```http
GET /jobs/sources
```

**Response:**

```json
{
  "success": true,
  "enabled_sources": ["RemoteOK", "GitHub", "Reed", "Adzuna"],
  "available_sources": {
    "remoteok": {
      "name": "RemoteOK",
      "enabled": true,
      "description": "Remote job listings from RemoteOK.com",
      "api_type": "REST API",
      "rate_limit": "No authentication required"
    }
  }
}
```

## 🎯 Project Matching Endpoints

### Match Projects to Job

```http
GET /match/{job_id}
```

**Query Parameters:**

- `user_id` (string, required): User ID for project matching
- `algorithm` (string, default: "tfidf"): Matching algorithm
- `max_results` (int, default: 5): Maximum results to return
- `use_cache` (bool, default: true): Whether to use cached results

**Response:**

```json
{
  "success": true,
  "job_id": "job-uuid",
  "user_id": "user-uuid",
  "algorithm_used": "TF-IDF + Keyword Matching",
  "execution_time_ms": 245.7,
  "cache_hit": false,
  "matches": [
    {
      "project_id": "project-uuid",
      "project_title": "E-commerce Platform",
      "confidence_score": 0.87,
      "confidence_percentage": 87.0,
      "matching_keywords": ["python", "fastapi", "postgresql"],
      "explanation": {
        "algorithm": "TF-IDF + Keyword Matching",
        "tfidf_similarity": 0.75,
        "keyword_match_score": 0.92,
        "technology_match_score": 0.85
      }
    }
  ]
}
```

### Explain Project Match

```http
POST /match/{job_id}/explain
```

**Query Parameters:**

- `project_id` (string, required): Project ID to explain
- `user_id` (string, required): User ID

**Response:**

```json
{
  "success": true,
  "job_title": "Senior Python Developer",
  "project_title": "E-commerce Platform",
  "confidence_score": 0.87,
  "confidence_percentage": 87.0,
  "detailed_explanation": {
    "matching_technologies": ["python", "fastapi", "postgresql"],
    "matching_keywords": ["api", "backend", "database"],
    "missing_required_skills": ["docker", "aws"]
  },
  "recommendations": [
    "Excellent match! This project strongly aligns with the job requirements.",
    "Consider highlighting Docker and AWS experience if available."
  ]
}
```

## 📄 Resume Generation Endpoints

### Generate Resume

```http
POST /resume/generate
```

**Request Body:**

```json
{
  "name": "John Doe",
  "phone": "+1(555) 123-4567",
  "location": "San Francisco, CA",
  "email": "john@example.com",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "website_url": "https://johndoe.dev",
  "experience_years": "5+",
  "primary_skills": ["Python", "React", "AWS"],
  "education": [
    {
      "degree": "Bachelor of Computer Science",
      "institution": "Stanford University",
      "year": "2018-2022",
      "coursework": "Data Structures, Algorithms, Machine Learning"
    }
  ],
  "skills": [
    {
      "category": "Programming Languages",
      "items": ["Python", "JavaScript", "TypeScript"]
    }
  ],
  "experience": [
    {
      "role": "Software Engineer",
      "company": "TechCorp",
      "duration": "2022-Present",
      "location": "San Francisco, CA",
      "achievements": [
        "Built scalable APIs serving 100K+ users",
        "Reduced response times by 60%"
      ]
    }
  ],
  "projects": [
    {
      "title": "E-commerce Platform",
      "description": "Built using Python, FastAPI, and React..."
    }
  ],
  "job_id": "optional-job-uuid-for-customization"
}
```

**Response:**

```json
{
  "success": true,
  "resume_id": "resume-uuid",
  "download_url": "/api/v1/resume/download/resume-uuid",
  "generation_method": "latex",
  "message": "Resume generated successfully using latex"
}
```

### Download Resume

```http
GET /resume/download/{resume_id}
```

**Response:** PDF file download

## ✉️ Cover Letter Generation Endpoints

### Generate Cover Letter for Job

```http
POST /cover-letters/{job_id}
```

**Request Body:**

```json
{
  "user_id": "user-uuid",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "user_phone": "+1(555) 123-4567",
  "user_location": "San Francisco, CA",
  "experience_years": "5+",
  "primary_skills": ["Python", "React", "AWS"],
  "selected_projects": [
    {
      "title": "E-commerce Platform",
      "description": "Built using Python and FastAPI..."
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "cover_letter_id": "cover-letter-uuid",
  "content": "Dear Hiring Manager,\n\nI am writing to express...",
  "download_url": "/api/v1/cover-letters/cover-letter-uuid/download",
  "generation_method": "ai",
  "message": "Cover letter generated using ai"
}
```

### Bulk Cover Letter Generation

```http
POST /cover-letters/bulk
```

**Request Body:**

```json
{
  "user_id": "user-uuid",
  "job_ids": ["job-uuid-1", "job-uuid-2", "job-uuid-3"],
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "primary_skills": ["Python", "React", "AWS"]
}
```

**Response:**

```json
{
  "success": true,
  "total_requested": 3,
  "total_generated": 3,
  "total_failed": 0,
  "execution_time_seconds": 8.45,
  "results": [
    {
      "job_id": "job-uuid-1",
      "job_title": "Senior Python Developer",
      "company": "TechCorp",
      "cover_letter_id": "cover-letter-uuid-1",
      "download_url": "/api/v1/cover-letters/cover-letter-uuid-1/download",
      "generation_method": "ai",
      "status": "success"
    }
  ],
  "errors": []
}
```

### Download Cover Letter

```http
GET /cover-letters/{cover_letter_id}/download
```

**Response:** Text file download

### Bulk Download Cover Letters

```http
POST /cover-letters/bulk/download
```

**Query Parameters:**

- `cover_letter_ids` (array): List of cover letter IDs to download

**Response:** ZIP file download containing all cover letters

## 📊 System Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "job-application-system",
  "version": "1.0.0"
}
```

### Cache Statistics

```http
GET /match/cache/stats
```

**Response:**

```json
{
  "success": true,
  "cache_stats": {
    "memory_cache_size": 45,
    "redis_available": true,
    "redis_used_memory": "2.1MB",
    "redis_connected_clients": 3
  }
}
```

## 🔒 Authentication

Currently, the API uses simple `user_id` based identification. For production deployment, implement proper authentication:

```http
Authorization: Bearer <jwt_token>
```

## 📝 Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

**Common Status Codes:**

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error (invalid request body)
- `500` - Internal Server Error

## 🚀 Rate Limits

- **Job Fetching**: Limited by external APIs (Reed: 1000/month, Adzuna: 1000/month)
- **Resume Generation**: No limits (local processing)
- **Cover Letter Generation**: Limited by AI API quotas
- **Project Matching**: Cached results improve performance

## 📈 Performance Tips

1. **Use Caching**: Enable Redis for better project matching performance
2. **Bulk Operations**: Use bulk endpoints for multiple cover letters
3. **Pagination**: Use limit/offset for large job result sets
4. **Keywords**: Specific keywords improve job fetching relevance

---

**Interactive API Documentation available at:** `http://localhost:8000/docs`
