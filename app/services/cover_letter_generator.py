"""
Cover Letter Generation Service

Generates personalized cover letters using AI (Groq/OpenAI) with template fallbacks.
Supports both individual and bulk generation with proper error handling.
"""

import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from loguru import logger

# Optional AI dependencies
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class CoverLetterGenerationError(Exception):
    """Raised when cover letter generation fails."""
    pass


class CoverLetterGenerator:
    """
    Cover Letter Generation Service
    
    Features:
    - AI generation using Groq (primary) or OpenAI (fallback)
    - Template-based generation when AI unavailable
    - File storage and retrieval
    - Bulk generation support
    """
    
    def __init__(self):
        """Initialize the cover letter generator with AI clients and templates."""
        self.template_dir = Path("app/templates")
        self.output_dir = Path("app/generated/cover_letters")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 template engine
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Initialize AI clients
        self._setup_ai_clients()
        
        logger.info(f"Cover letter generator initialized - AI available: {self.ai_available}")
    
    def _setup_ai_clients(self):
        """Initialize AI service clients."""
        self.ai_available = False
        self.groq_client = None
        self.openai_client = None
        
        # Setup Groq (preferred for speed)
        groq_key = os.getenv("GROQ_API_KEY")
        if GROQ_AVAILABLE and groq_key and groq_key != "your-groq-api-key-here":
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.ai_available = True
                logger.info("Groq client initialized")
            except Exception as e:
                logger.warning(f"Groq setup failed: {e}")
        
        # Setup OpenAI as fallback
        openai_key = os.getenv("OPENAI_API_KEY")
        if OPENAI_AVAILABLE and openai_key and openai_key != "your-openai-api-key-here":
            try:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                self.ai_available = True
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI setup failed: {e}")
    
    def generate_cover_letter(
        self,
        job_data: Dict[str, Any],
        user_data: Dict[str, Any],
        selected_projects: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized cover letter.
        
        Args:
            job_data: Job information (title, company, description, requirements)
            user_data: User profile data
            selected_projects: Relevant projects to highlight
            
        Returns:
            Dict with cover_letter_id, content, and generation_method
        """
        try:
            cover_letter_id = str(uuid.uuid4())
            
            # Try AI generation first, fallback to template
            if self.ai_available:
                try:
                    content = self._generate_with_ai(job_data, user_data, selected_projects)
                    method = "ai"
                except Exception as e:
                    logger.warning(f"AI generation failed: {e}, using template")
                    content = self._generate_with_template(job_data, user_data, selected_projects)
                    method = "template"
            else:
                content = self._generate_with_template(job_data, user_data, selected_projects)
                method = "template"
            
            # Save to file
            file_path = self._save_cover_letter(cover_letter_id, content)
            
            return {
                "cover_letter_id": cover_letter_id,
                "content": content,
                "file_path": str(file_path),
                "generation_method": method,
                "created_at": datetime.utcnow().isoformat(),
                "job_title": job_data.get("title", "Position"),
                "company": job_data.get("company", "Company")
            }
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            raise CoverLetterGenerationError(f"Failed to generate cover letter: {str(e)}")
    
    def _generate_with_ai(
        self,
        job_data: Dict[str, Any],
        user_data: Dict[str, Any],
        selected_projects: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate cover letter using AI services."""
        
        prompt = self._build_ai_prompt(job_data, user_data, selected_projects)
        
        # Try Groq first (faster)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a professional career advisor who writes compelling cover letters."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq generation failed: {e}")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional career advisor who writes compelling cover letters."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")
        
        raise Exception("No AI service available")
    
    def _build_ai_prompt(
        self,
        job_data: Dict[str, Any],
        user_data: Dict[str, Any],
        selected_projects: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build AI prompt for cover letter generation."""
        
        # Extract key information
        job_title = job_data.get("title", "Position")
        company = job_data.get("company", "Company")
        job_description = job_data.get("description", "")
        requirements = job_data.get("requirements", [])
        
        user_name = user_data.get("name", "Candidate")
        experience = user_data.get("experience", [])
        skills = user_data.get("primary_skills", [])
        
        # Build project highlights
        project_highlights = ""
        if selected_projects:
            project_highlights = "\\n\\nRelevant Projects:\\n"
            for project in selected_projects[:2]:  # Top 2 projects
                project_highlights += f"- {project.get('title', '')}: {project.get('description', '')[:100]}...\\n"
        
        prompt = f"""
Write a professional cover letter for the following job application:

Job Details:
- Position: {job_title}
- Company: {company}
- Key Requirements: {', '.join(requirements[:5])}

Candidate Profile:
- Name: {user_name}
- Key Skills: {', '.join(skills[:5])}
- Years of Experience: {user_data.get('experience_years', '2+')}
{project_highlights}

Requirements:
1. Keep it concise (3-4 paragraphs, ~300 words)
2. Show enthusiasm for the role and company
3. Highlight relevant skills and experience
4. Include specific examples from projects when possible
5. Professional but personable tone
6. Include proper business letter format with date and addresses

Format the letter as a complete business letter ready to send.
"""
        
        return prompt
    
    def _generate_with_template(
        self,
        job_data: Dict[str, Any],
        user_data: Dict[str, Any],
        selected_projects: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate cover letter using Jinja2 template."""
        
        try:
            template = self.jinja_env.get_template("cover_letter_template.txt")
        except Exception:
            # Create default template if not found
            template_content = self._get_default_template()
            template_path = self.template_dir / "cover_letter_template.txt"
            template_path.write_text(template_content)
            template = self.jinja_env.get_template("cover_letter_template.txt")
        
        # Prepare template data
        template_data = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "user_name": user_data.get("name", "Your Name"),
            "user_address": user_data.get("location", "Your Address"),
            "user_email": user_data.get("email", "your.email@example.com"),
            "user_phone": user_data.get("phone", "Your Phone"),
            "company": job_data.get("company", "Company Name"),
            "job_title": job_data.get("title", "Position Title"),
            "hiring_manager": "Hiring Manager",  # Could be enhanced to extract from job posting
            "experience_years": user_data.get("experience_years", "2+"),
            "key_skills": ", ".join(user_data.get("primary_skills", ["relevant skills"])[:3]),
            "project_highlight": self._get_project_highlight(selected_projects),
            "requirements_match": self._match_requirements(job_data, user_data)
        }
        
        return template.render(**template_data)
    
    def _get_project_highlight(self, selected_projects: Optional[List[Dict[str, Any]]]) -> str:
        """Get a highlight from the most relevant project."""
        if not selected_projects:
            return "my recent projects have involved building scalable applications"
        
        project = selected_projects[0]
        title = project.get("title", "Recent Project")
        description = project.get("description", "")[:150]
        
        return f"my {title} project, where {description.lower()}"
    
    def _match_requirements(self, job_data: Dict[str, Any], user_data: Dict[str, Any]) -> str:
        """Find matching requirements between job and user skills."""
        job_requirements = [req.lower() for req in job_data.get("requirements", [])]
        user_skills = [skill.lower() for skill in user_data.get("primary_skills", [])]
        
        matches = [skill for skill in user_skills if any(req in skill or skill in req for req in job_requirements)]
        
        if matches:
            return f"particularly in {', '.join(matches[:3])}"
        return "across various technologies"
    
    def _save_cover_letter(self, cover_letter_id: str, content: str) -> Path:
        """Save cover letter content to file."""
        file_path = self.output_dir / f"cover_letter_{cover_letter_id}.txt"
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def _get_default_template(self) -> str:
        """Default cover letter template."""
        return """{{ date }}

{{ user_name }}
{{ user_address }}
{{ user_email }}
{{ user_phone }}

{{ hiring_manager }}
{{ company }}

Dear {{ hiring_manager }},

I am writing to express my strong interest in the {{ job_title }} position at {{ company }}. With {{ experience_years }} years of experience in software development and expertise in {{ key_skills }}, I am excited about the opportunity to contribute to your team.

In my previous roles, I have successfully delivered projects that align well with your requirements, {{ requirements_match }}. For example, {{ project_highlight }}, demonstrating my ability to build robust solutions that drive business value.

What particularly attracts me to {{ company }} is your commitment to innovation and technical excellence. I am eager to bring my passion for clean code, problem-solving, and collaborative development to help {{ company }} achieve its goals.

I would welcome the opportunity to discuss how my experience and enthusiasm can contribute to your team. Thank you for considering my application.

Sincerely,
{{ user_name }}"""
    
    def get_cover_letter_path(self, cover_letter_id: str) -> Optional[Path]:
        """Get file path for a generated cover letter."""
        file_path = self.output_dir / f"cover_letter_{cover_letter_id}.txt"
        return file_path if file_path.exists() else None
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up old cover letter files."""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        for file_path in self.output_dir.glob("cover_letter_*.txt"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logger.info(f"Cleaned up old cover letter: {file_path.name}")


# Global instance
cover_letter_generator = CoverLetterGenerator()