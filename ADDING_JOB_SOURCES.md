# 🔌 Adding More Job APIs

## 🎯 Current Status

**Currently Active:**
- ✅ **RemoteOK** - Working, fetching real jobs
- ✅ **GitHub Jobs** - Searches GitHub repos for hiring info
- ✅ **Reed** - UK job listings (requires API key)
- ✅ **Adzuna** - Global job listings (requires API credentials)
- 🚧 **Indeed** - Placeholder (requires web scraping)
- 🚧 **AngelList** - Placeholder (requires web scraping)

## 🚀 How to Add New Job Sources

### 1. Create a New Fetcher Class

Add to `app/services/job_fetcher.py`:

```python
class YourJobSiteFetcher(JobFetcher):
    """Job fetcher for YourJobSite."""
    
    def __init__(self):
        self.base_url = "https://api.yourjobsite.com"
        self.source_name = "YourJobSite"
    
    def get_source_name(self) -> str:
        return self.source_name
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        """Fetch jobs from YourJobSite API."""
        try:
            # Your API integration logic here
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/jobs",
                    params={"q": " ".join(keywords), "limit": limit},
                    headers={"Authorization": "Bearer YOUR_API_KEY"}
                )
                
                jobs_data = response.json()
                return [self._parse_job(job) for job in jobs_data["jobs"]]
                
        except Exception as e:
            logger.error(f"YourJobSite fetching failed: {e}")
            return []
    
    def _parse_job(self, job_data: dict) -> JobCreate:
        """Parse job data from API response."""
        return JobCreate(
            title=job_data["title"],
            company=job_data["company"],
            description=job_data["description"],
            location=job_data.get("location", "Remote"),
            requirements=job_data.get("skills", []),
            source=self.source_name,
            external_id=str(job_data["id"])
        )
```

### 2. Register in Source Manager

Add to `app/services/job_source_config.py`:

```python
"yourjobsite": {
    "name": "YourJobSite",
    "class": YourJobSiteFetcher,
    "enabled": True,
    "description": "Jobs from YourJobSite.com",
    "api_type": "REST API",
    "rate_limit": "1000 requests/hour"
}
```

### 3. Test Your New Source

```bash
# Test the new source
python -c "
from app.services.job_source_config import job_source_manager
sources = job_source_manager.get_enabled_source_names()
print('Enabled sources:', sources)
"
```

## 📋 Popular Job APIs to Add

### 1. **Adzuna API** (Recommended)
- **URL**: https://developer.adzuna.com/
- **Type**: REST API with free tier
- **Coverage**: Global job listings
- **Rate Limit**: 1000 calls/month (free)

### 2. **JSearch (RapidAPI)** (Recommended)
- **URL**: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- **Type**: REST API
- **Coverage**: Google for Jobs data
- **Rate Limit**: 150 requests/month (free)

### 3. **Reed API** (UK Jobs)
- **URL**: https://www.reed.co.uk/developers
- **Type**: REST API
- **Coverage**: UK job market
- **Rate Limit**: Good for UK-focused searches

### 4. **Glassdoor API** (Limited)
- **URL**: Partner program only
- **Type**: Partner API
- **Coverage**: Company reviews + some jobs

### 5. **LinkedIn Jobs** (Complex)
- **URL**: No public API
- **Type**: Web scraping (complex)
- **Coverage**: Professional network jobs

## 🛠️ Implementation Examples

### Reed API Implementation (✅ Implemented)

```python
class ReedFetcher(JobFetcher):
    def __init__(self):
        self.base_url = "https://www.reed.co.uk/api/1.0"
        self.api_key = os.getenv("REED_API_KEY")
        self.source_name = "Reed"
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        search_params = {
            "keywords": " ".join(keywords),
            "locationName": "Remote",
            "permanent": "true",
            "resultsToTake": min(limit, 100)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search",
                params=search_params,
                auth=(self.api_key, "")  # Basic auth with API key
            )
            data = response.json()
            return [self._parse_reed_job(job) for job in data.get("results", [])]
```

**To enable Reed:**
```bash
# Set your Reed API key
export REED_API_KEY="your_reed_api_key_here"

# Enable Reed source
curl -X POST http://localhost:8000/api/v1/jobs/sources/reed/toggle?enable=true
```

### Adzuna API Implementation (✅ Implemented)

```python
class AdzunaFetcher(JobFetcher):
    def __init__(self):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.source_name = "Adzuna"
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        search_url = f"{self.base_url}/us/search/1"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": " ".join(keywords),
            "where": "remote",
            "results_per_page": min(limit, 50)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params)
            data = response.json()
            
            return [self._parse_adzuna_job(job) for job in data.get("results", [])]
```

**To enable Adzuna:**
```bash
# Set your Adzuna API credentials
export ADZUNA_APP_ID="your_app_id_here"
export ADZUNA_APP_KEY="your_app_key_here"

# Enable Adzuna source
curl -X POST http://localhost:8000/api/v1/jobs/sources/adzuna/toggle?enable=true
```

### JSearch (RapidAPI) Implementation

```python
class JSearchFetcher(JobFetcher):
    def __init__(self):
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.source_name = "JSearch"
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        search_url = f"{self.base_url}/search"
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        params = {
            "query": " ".join(keywords) + " remote",
            "page": "1",
            "num_pages": "1"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=headers)
            data = response.json()
            
            return [self._parse_jsearch_job(job) for job in data.get("data", [])]
```

## 🔧 Managing Job Sources

### View Available Sources
```bash
GET /api/v1/jobs/sources
```

### Enable/Disable Sources
```bash
POST /api/v1/jobs/sources/indeed/toggle?enable=true
POST /api/v1/jobs/sources/angellist/toggle?enable=false
```

### Test Multi-Source Fetching
```bash
POST /api/v1/jobs/fetch
{
  "keywords": ["python", "react"],
  "limit_per_source": 10
}
```

## 📊 Expected Multi-Source Results

With multiple sources enabled, you'll see:

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
      "Adzuna": {"fetched": 5, "new": 4, "updated": 1, "status": "success"}
    },
    "errors": []
  }
}
```

## 🚨 Important Considerations

### Rate Limiting
- Each API has different rate limits
- Implement delays between requests
- Use API keys when available
- Monitor usage to avoid blocking

### Legal & Ethical
- Respect robots.txt for web scraping
- Follow API terms of service
- Don't overload servers
- Consider caching to reduce requests

### Data Quality
- Different APIs return different data formats
- Implement robust parsing for each source
- Handle missing fields gracefully
- Deduplicate across sources

## 🔑 Getting API Keys

### Reed API Key
1. Visit https://www.reed.co.uk/developers
2. Sign up for a free developer account
3. Get your API key from the dashboard
4. Free tier: 1000 requests per month

### Adzuna API Credentials
1. Visit https://developer.adzuna.com/
2. Sign up for a free developer account
3. Create an app to get your App ID and App Key
4. Free tier: 1000 calls per month

### Environment Variables
Add to your `.env` file or environment:
```bash
# Reed API
REED_API_KEY=your_reed_api_key_here

# Adzuna API
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here
```

## 🎯 Quick Start: Enable All Sources

Multiple job sources are now implemented and ready to use:

```bash
# Start server
python start_server.py

# Check current sources
curl http://localhost:8000/api/v1/jobs/sources

# Enable Reed (if you have API key)
curl -X POST "http://localhost:8000/api/v1/jobs/sources/reed/toggle?enable=true"

# Enable Adzuna (if you have API credentials)
curl -X POST "http://localhost:8000/api/v1/jobs/sources/adzuna/toggle?enable=true"

# Fetch from multiple sources
curl -X POST http://localhost:8000/api/v1/jobs/fetch \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["python", "javascript"], "limit_per_source": 5}'
```

You should see jobs from RemoteOK, GitHub, Reed, and Adzuna in the results! 🚀

### Expected Multi-Source Output
```json
{
  "success": true,
  "message": "Fetched 35 jobs, 28 new, 7 updated",
  "results": {
    "total_fetched": 35,
    "new_jobs": 28,
    "updated_jobs": 7,
    "sources": {
      "RemoteOK": {"fetched": 8, "new": 6, "updated": 2, "status": "success"},
      "GitHub": {"fetched": 12, "new": 10, "updated": 2, "status": "success"},
      "Reed": {"fetched": 10, "new": 8, "updated": 2, "status": "success"},
      "Adzuna": {"fetched": 5, "new": 4, "updated": 1, "status": "success"}
    },
    "errors": []
  }
}
```