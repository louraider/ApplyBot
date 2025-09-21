"""
Generic job fetcher interface and implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger
import os
from dotenv import load_dotenv
from app.schemas.job import JobCreate

# Load environment variables
load_dotenv()


class JobFetcher(ABC):
    @abstractmethod
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        pass


class RemoteOKFetcher(JobFetcher):
    """Job fetcher for RemoteOK API."""
    
    def __init__(self):
        self.base_url = "https://remoteok.com/api" #RemoteOk API
        self.source_name = "RemoteOK"
    
    def get_source_name(self) -> str:
        return self.source_name
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        """
        Fetch jobs from RemoteOK API.
        
        RemoteOK API returns jobs in JSON format without authentication.
        """
        try:
            logger.info(f"Fetching jobs from RemoteOK with keywords: {keywords}")
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # RemoteOK API endpoint
                response = await client.get(
                    self.base_url,
                    headers={
                        "User-Agent": "JobApplicationSystem/1.0 (Educational Project)",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                
                # RemoteOK returns JSON array, first item is metadata
                jobs_data = response.json()
                
                # Skip first item (metadata) and process jobs
                raw_jobs = jobs_data[1:] if len(jobs_data) > 1 else []
                
                logger.info(f"Retrieved {len(raw_jobs)} jobs from RemoteOK")
                
                # Parse and filter jobs
                parsed_jobs = []
                for job_data in raw_jobs[:limit]:
                    try:
                        job = self._parse_job_data(job_data, keywords)
                        if job:
                            parsed_jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse job: {e}")
                        continue
                
                logger.info(f"Parsed {len(parsed_jobs)} relevant jobs")
                return parsed_jobs
                
        except httpx.TimeoutException:
            logger.error("RemoteOK API request timed out")
            raise Exception("Job fetching timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"RemoteOK API error: {e.response.status_code}")
            raise Exception(f"Job API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error fetching jobs: {e}")
            raise Exception(f"Job fetching failed: {str(e)}")
    
    def _parse_job_data(self, job_data: Dict[str, Any], keywords: List[str]) -> Optional[JobCreate]:
        """
        Parse RemoteOK job data into JobCreate object.
        
        Args:
            job_data: Raw job data from RemoteOK API
            keywords: Keywords to filter by
            
        Returns:
            JobCreate object if job matches criteria, None otherwise
        """
        try:
            # Extract basic job information
            title = job_data.get("position", "").strip()
            company = job_data.get("company", "").strip()
            description = job_data.get("description", "").strip()
            
            # Skip jobs without essential information
            if not title or not company:
                return None
            
            # Filter by keywords if provided
            if keywords and not self._matches_keywords(job_data, keywords):
                return None
            
            # Extract additional fields
            location = self._extract_location(job_data)
            salary_range = self._extract_salary(job_data)
            requirements = self._extract_requirements(job_data)
            application_email = job_data.get("apply_url", "")
            
            # Convert posted date
            posted_date = None
            if job_data.get("date"):
                try:
                    # RemoteOK uses Unix timestamp
                    posted_date = datetime.fromtimestamp(int(job_data["date"]))
                except (ValueError, TypeError):
                    pass
            
            return JobCreate(
                title=title,
                company=company,
                description=description,
                location=location,
                salary_range=salary_range,
                requirements=requirements,
                application_email=application_email,
                source=self.source_name,
                external_id=str(job_data.get("id", "")),
                posted_date=posted_date
            )
            
        except Exception as e:
            logger.warning(f"Error parsing job data: {e}")
            return None
    
    def _matches_keywords(self, job_data: Dict[str, Any], keywords: List[str]) -> bool:
        """Check if job matches any of the provided keywords."""
        if not keywords:
            return True
        
        # Combine searchable text
        searchable_text = " ".join([
            job_data.get("position", ""),
            job_data.get("company", ""),
            job_data.get("description", ""),
            " ".join(job_data.get("tags", []))
        ]).lower()
        
        # Check if any keyword matches
        return any(keyword.lower() in searchable_text for keyword in keywords)
    
    def _extract_location(self, job_data: Dict[str, Any]) -> str:
        """Extract location information."""
        location_parts = []
        
        if job_data.get("location"):
            location_parts.append(job_data["location"])
        
        # RemoteOK often has "Worldwide" or specific locations
        if not location_parts:
            location_parts.append("Remote")
        
        return ", ".join(location_parts)
    
    def _extract_salary(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Extract salary information if available."""
        # RemoteOK sometimes includes salary in description or tags
        salary_indicators = ["salary", "$", "usd", "eur", "k/year", "per year"]
        
        description = job_data.get("description", "").lower()
        for indicator in salary_indicators:
            if indicator in description:
                # Try to extract salary range (basic implementation)
                # This could be enhanced with regex patterns
                return "See job description"
        
        return None
    
    def _extract_requirements(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract job requirements and skills."""
        requirements = []
        
        # RemoteOK provides tags which are often skills/requirements
        if job_data.get("tags"):
            requirements.extend(job_data["tags"])
        
        # Extract common tech keywords from description
        description = job_data.get("description", "").lower()
        tech_keywords = [
            "python", "javascript", "react", "node.js", "java", "go", "rust",
            "docker", "kubernetes", "aws", "gcp", "azure", "sql", "mongodb",
            "postgresql", "redis", "git", "ci/cd", "agile", "scrum"
        ]
        
        for keyword in tech_keywords:
            if keyword in description and keyword not in requirements:
                requirements.append(keyword.title())
        
        return requirements[:10]  # Limit to 10 requirements



class ReedFetcher(JobFetcher):
    """Job fetcher for Reed.co.uk API."""
    
    def __init__(self):
        self.base_url = "https://www.reed.co.uk/api/1.0"
        self.source_name = "Reed"
        # Get API key from environment or config
        self.api_key = os.getenv("REED_API_KEY", "YOUR_REED_API_KEY_HERE")
    
    def get_source_name(self) -> str:
        return self.source_name
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        """
        Fetch jobs from Reed.co.uk API.
        
        Reed API Documentation: https://www.reed.co.uk/developers
        Free tier: 1000 requests per month
        """
        try:
            logger.info(f"Fetching jobs from Reed with keywords: {keywords}")
            
            if self.api_key == "YOUR_REED_API_KEY_HERE":
                logger.warning("Reed API key not configured - skipping Reed jobs")
                return []
            
            # Construct search parameters
            search_params = {
                "keywords": " ".join(keywords) if keywords else "",
                "locationName": "Remote",
                "distanceFromLocation": 15,
                "permanent": "true",
                "resultsToTake": min(limit, 100),  # Reed max is 100
                "resultsToSkip": 0
            }
            
            # Remove empty parameters
            search_params = {k: v for k, v in search_params.items() if v}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=search_params,
                    auth=(self.api_key, ""),  # Reed uses basic auth with API key as username
                    headers={
                        "User-Agent": "JobApplicationSystem/1.0"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                jobs_data = data.get("results", [])
                
                logger.info(f"Retrieved {len(jobs_data)} jobs from Reed")
                
                # Parse jobs
                parsed_jobs = []
                for job_data in jobs_data:
                    try:
                        job = self._parse_reed_job(job_data)
                        if job:
                            parsed_jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse Reed job: {e}")
                        continue
                
                logger.info(f"Parsed {len(parsed_jobs)} Reed jobs")
                return parsed_jobs
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Reed API authentication failed - check API key")
            else:
                logger.error(f"Reed API error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Reed fetching failed: {e}")
            return []
    
    def _parse_reed_job(self, job_data: Dict[str, Any]) -> Optional[JobCreate]:
        """Parse Reed job data into JobCreate object."""
        try:
            title = job_data.get("jobTitle", "").strip()
            company = job_data.get("employerName", "").strip()
            description = job_data.get("jobDescription", "").strip()
            
            if not title or not company:
                return None
            
            # Extract location
            location = job_data.get("locationName", "UK")
            
            # Extract salary
            salary_range = None
            salary_min = job_data.get("minimumSalary")
            salary_max = job_data.get("maximumSalary")
            if salary_min and salary_max:
                salary_range = f"£{salary_min:,} - £{salary_max:,}"
            elif salary_min:
                salary_range = f"£{salary_min:,}+"
            
            # Extract requirements from description
            requirements = self._extract_reed_requirements(description)
            
            # Application URL
            application_url = job_data.get("jobUrl", "")
            
            # Posted date
            posted_date = None
            if job_data.get("date"):
                try:
                    posted_date = datetime.fromisoformat(job_data["date"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            return JobCreate(
                title=title,
                company=company,
                description=description,
                location=location,
                salary_range=salary_range,
                requirements=requirements,
                application_email=application_url,
                source=self.source_name,
                external_id=str(job_data.get("jobId", "")),
                posted_date=posted_date
            )
            
        except Exception as e:
            logger.warning(f"Error parsing Reed job data: {e}")
            return None
    
    def _extract_reed_requirements(self, description: str) -> List[str]:
        """Extract requirements from Reed job description."""
        requirements = []
        
        # Common tech keywords to look for
        tech_keywords = [
            "python", "javascript", "java", "c#", "php", "ruby", "go", "rust",
            "react", "vue", "angular", "node.js", "django", "flask", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
            "sql", "postgresql", "mysql", "mongodb", "redis",
            "git", "ci/cd", "jenkins", "gitlab", "github"
        ]
        
        description_lower = description.lower()
        for keyword in tech_keywords:
            if keyword in description_lower:
                requirements.append(keyword.title())
        
        return requirements[:10]  # Limit to 10 requirements
    
class AdzunaFetcher(JobFetcher):
    """Job fetcher for Adzuna API."""
    
    def __init__(self):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.source_name = "Adzuna"
        # Get API credentials from environment
        self.app_id = os.getenv("ADZUNA_APP_ID", "YOUR_ADZUNA_APP_ID_HERE")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "YOUR_ADZUNA_APP_KEY_HERE")
        self.country = "us"  # Default to US, can be configured
    
    def get_source_name(self) -> str:
        return self.source_name
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        """
        Fetch jobs from Adzuna API.
        
        Adzuna API Documentation: https://developer.adzuna.com/
        Free tier: 1000 calls per month
        """
        try:
            logger.info(f"Fetching jobs from Adzuna with keywords: {keywords}")
            
            if (self.app_id == "YOUR_ADZUNA_APP_ID_HERE" or 
                self.app_key == "YOUR_ADZUNA_APP_KEY_HERE"):
                logger.warning("Adzuna API credentials not configured - skipping Adzuna jobs")
                return []
            
            # Adzuna search endpoint
            search_url = f"{self.base_url}/{self.country}/search/1"
            
            # Search parameters
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "results_per_page": min(limit, 50),  # Adzuna max is 50
                "what": " ".join(keywords) if keywords else "",
                "content-type": "application/json"
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    search_url,
                    params=params,
                    headers={
                        "User-Agent": "JobApplicationSystem/1.0"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                jobs_data = data.get("results", [])
                
                logger.info(f"Retrieved {len(jobs_data)} jobs from Adzuna")
                
                # Parse jobs
                parsed_jobs = []
                for job_data in jobs_data:
                    try:
                        job = self._parse_adzuna_job(job_data)
                        if job:
                            parsed_jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse Adzuna job: {e}")
                        continue
                
                logger.info(f"Parsed {len(parsed_jobs)} Adzuna jobs")
                return parsed_jobs
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Adzuna API authentication failed - check app_id and app_key")
            elif e.response.status_code == 429:
                logger.error("Adzuna API rate limit exceeded")
            else:
                logger.error(f"Adzuna API error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Adzuna fetching failed: {e}")
            return []
    
    def _parse_adzuna_job(self, job_data: Dict[str, Any]) -> Optional[JobCreate]:
        """Parse Adzuna job data into JobCreate object."""
        try:
            title = job_data.get("title", "").strip()
            company = job_data.get("company", {}).get("display_name", "").strip()
            description = job_data.get("description", "").strip()
            
            if not title or not company:
                return None
            
            # Extract location
            location_data = job_data.get("location", {})
            location_parts = []
            if location_data.get("display_name"):
                location_parts.append(location_data["display_name"])
            if not location_parts:
                location_parts.append("Remote")
            location = ", ".join(location_parts)
            
            # Extract salary
            salary_range = None
            salary_min = job_data.get("salary_min")
            salary_max = job_data.get("salary_max")
            if salary_min and salary_max:
                salary_range = f"${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min:
                salary_range = f"${salary_min:,.0f}+"
            
            # Extract requirements from description and category
            requirements = self._extract_adzuna_requirements(job_data)
            
            # Application URL
            application_url = job_data.get("redirect_url", "")
            
            # Posted date
            posted_date = None
            if job_data.get("created"):
                try:
                    posted_date = datetime.fromisoformat(job_data["created"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
            return JobCreate(
                title=title,
                company=company,
                description=description,
                location=location,
                salary_range=salary_range,
                requirements=requirements,
                application_email=application_url,
                source=self.source_name,
                external_id=str(job_data.get("id", "")),
                posted_date=posted_date
            )
            
        except Exception as e:
            logger.warning(f"Error parsing Adzuna job data: {e}")
            return None
    
    def _extract_adzuna_requirements(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract requirements from Adzuna job data."""
        requirements = []
        
        # Add category as a requirement
        category = job_data.get("category", {}).get("label", "")
        if category:
            requirements.append(category)
        
        # Extract from description
        description = job_data.get("description", "").lower()
        tech_keywords = [
            "python", "javascript", "java", "c#", "php", "ruby", "go", "rust",
            "react", "vue", "angular", "node.js", "django", "flask", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
            "sql", "postgresql", "mysql", "mongodb", "redis",
            "git", "ci/cd", "jenkins", "agile", "scrum"
        ]
        
        for keyword in tech_keywords:
            if keyword in description and keyword.title() not in requirements:
                requirements.append(keyword.title())
        
        return requirements[:10]  # Limit to 10 requirements

class GitHubJobsFetcher(JobFetcher):
    """Job fetcher for GitHub Jobs (using GitHub's search API for repositories with job postings)."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.source_name = "GitHub"
    
    def get_source_name(self) -> str:
        return self.source_name
    
    async def fetch_jobs(self, keywords: List[str], limit: int = 50) -> List[JobCreate]:
        """
        Fetch tech jobs from GitHub repositories and organizations.
        
        This searches for repositories with job-related content and hiring information.
        """
        try:
            logger.info(f"Fetching jobs from GitHub with keywords: {keywords}")
            
            jobs = []
            
            # Search for repositories with job postings
            search_queries = [
                "hiring remote developer",
                "jobs remote engineer",
                "careers remote position"
            ]
            
            if keywords:
                # Add keyword-specific searches
                for keyword in keywords[:3]:  # Limit to avoid rate limiting
                    search_queries.append(f"hiring {keyword} remote")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for query in search_queries[:2]:  # Limit queries to avoid rate limiting
                    try:
                        response = await client.get(
                            f"{self.base_url}/search/repositories",
                            params={
                                "q": query,
                                "sort": "updated",
                                "order": "desc",
                                "per_page": min(10, limit)
                            },
                            headers={
                                "Accept": "application/vnd.github.v3+json",
                                "User-Agent": "JobApplicationSystem/1.0"
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            repo_jobs = self._parse_github_repos(data.get("items", []), keywords)
                            jobs.extend(repo_jobs)
                            
                            if len(jobs) >= limit:
                                break
                                
                    except Exception as e:
                        logger.warning(f"GitHub search query failed: {e}")
                        continue
            
            logger.info(f"Found {len(jobs)} potential jobs from GitHub")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"GitHub fetching failed: {e}")
            return []
    
    def _parse_github_repos(self, repos: List[Dict[str, Any]], keywords: List[str]) -> List[JobCreate]:
        """Parse GitHub repository data for job information."""
        jobs = []
        
        for repo in repos:
            try:
                # Extract basic info
                title = f"Developer Position at {repo.get('owner', {}).get('login', 'Unknown')}"
                company = repo.get('owner', {}).get('login', 'GitHub Organization')
                description = repo.get('description', '') or f"Opportunity at {company}"
                
                # Skip if not relevant
                if not self._is_job_relevant(repo, keywords):
                    continue
                
                # Extract requirements from topics and language
                requirements = []
                if repo.get('topics'):
                    requirements.extend(repo['topics'][:5])
                if repo.get('language'):
                    requirements.append(repo['language'])
                
                job = JobCreate(
                    title=title,
                    company=company,
                    description=f"{description}\n\nRepository: {repo.get('html_url', '')}",
                    location="Remote",
                    salary_range=None,
                    requirements=requirements,
                    application_email=repo.get('html_url', ''),
                    source=self.source_name,
                    external_id=str(repo.get('id', '')),
                    posted_date=None
                )
                
                jobs.append(job)
                
            except Exception as e:
                logger.warning(f"Error parsing GitHub repo: {e}")
                continue
        
        return jobs
    
    def _is_job_relevant(self, repo: Dict[str, Any], keywords: List[str]) -> bool:
        """Check if repository is relevant for job searching."""
        # Check if repo has job-related keywords
        job_indicators = ["hiring", "jobs", "careers", "positions", "openings"]
        
        repo_text = " ".join([
            repo.get('name', ''),
            repo.get('description', ''),
            " ".join(repo.get('topics', []))
        ]).lower()
        
        # Must have job indicators
        has_job_indicator = any(indicator in repo_text for indicator in job_indicators)
        
        # Should match keywords if provided
        matches_keywords = True
        if keywords:
            matches_keywords = any(keyword.lower() in repo_text for keyword in keywords)
        
        return has_job_indicator and matches_keywords

