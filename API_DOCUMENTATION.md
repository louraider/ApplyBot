  "errors": []
}
```

Error example (207 Multi-Status with partial failures):
```
{
  "success": false,
  "total_requested": 3,
  "total_generated": 2,
  "total_failed": 1,
  "results": [ /* successful entries */ ],
  "errors": [
    {"job_id": "job-3", "detail": "Job not found", "status_code": 404}
  ]
}
```

---

### 10) Download Cover Letter
GET /cover-letters/{cover_letter_id}/download

curl example (text file):
```
COV_ID="cov-2b2e7d7a-9f6c-4f2e-9a3d-7c9e5f3d1b2a"

curl -L \
  -o cover_letter.txt \
  "http://localhost:8000/api/v1/cover-letters/${COV_ID}/download"
```

- 404 Not Found
```
{
  "detail": "Cover letter not found",
  "status_code": 404
}
```

---

## 📊 System Endpoints

### 11) Health Check
GET /health

curl example:
```
curl -s "http://localhost:8000/api/v1/health" -H "Accept: application/json"
```

Success response (200):
```
{
  "status": "healthy",
  "service": "job-application-system",
  "version": "1.0.0"
}
```

### 12) Cache Statistics
GET /match/cache/stats

curl example:
```
curl -s "http://localhost:8000/api/v1/match/cache/stats" -H "Accept: application/json"
```

Success response (200):
```
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

---

## 🔒 Authentication
If enabled, include a Bearer token:
```
Authorization: Bearer <jwt_token>
```

Auth error example (401):
```
{
  "detail": "Not authenticated",
  "status_code": 401
}
```

---

## 📝 Error Responses
All endpoints return consistent error responses like:
```
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

Common Status Codes:
- 200 - Success
- 201 - Created (where applicable)
- 207 - Multi-Status (partial success)
- 400 - Bad Request (invalid parameters)
- 401 - Unauthorized (missing/invalid token)
- 404 - Not Found (resource doesn't exist)
- 422 - Validation Error (invalid request body)
- 429 - Too Many Requests (rate limited)
- 500 - Internal Server Error

---

Notes:
- Replace localhost with your deployment host when applicable.
- Realistic sample data is provided in all examples above.
- Interactive API docs available at http://localhost:8000/docs
