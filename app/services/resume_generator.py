"""
Production-ready resume generation service.
Supports LaTeX and ReportLab PDF generation with proper error handling.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader
from loguru import logger
import uuid
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not installed - only LaTeX generation available")


class ResumeGenerationError(Exception):
    """Raised when resume generation fails."""
    pass


class ResumeGenerator:
    """Production resume generator with multiple PDF backends."""
    
    def __init__(self):
        self.template_dir = Path("app/templates")
        self.output_dir = Path("app/generated/resumes")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self.latex_available = self._check_latex_availability()
        
        logger.info(f"Resume generator ready - LaTeX: {self.latex_available}, ReportLab: {REPORTLAB_AVAILABLE}")
    
    def _check_latex_availability(self) -> bool:
        """Check if LaTeX (pdflatex) is available on the system."""
        try:
            result = subprocess.run(
                ["pdflatex", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def generate_resume(
    self,
    user_data: Dict[str, Any],
    selected_projects: Optional[List[Dict[str, Any]]] = None,
    job_context: Optional[Dict[str, Any]] = None,
    job_id: Optional[str] = None
) -> Dict[str, Any]:
        try:
            logger.info("Starting resume generation")
            
            # Create meaningful resume_id with job context
            if job_id:
                resume_id = job_id
            else:
                resume_id = str(uuid.uuid4())
            
            # Prepare template data
            template_data = self._prepare_template_data(
                user_data, selected_projects, job_context
            )
            
            # Try LaTeX first, then fallbacks
            if self.latex_available:
                try:
                    file_path = self._generate_with_latex(resume_id, template_data)
                    method = "latex"
                    logger.info("Resume generated successfully with LaTeX")
                except Exception as e:
                    logger.warning(f"LaTeX generation failed: {e}, trying fallback")
                    file_path = self._generate_with_fallback(resume_id, template_data)
                    method = "fallback"
            else:
                file_path = self._generate_with_fallback(resume_id, template_data)
                method = "fallback"
            
            # Return appropriate response based on whether job_id was provided
            result = {
                "resume_id": resume_id,
                "generation_method": method,
                "created_at": datetime.utcnow().isoformat(),
                "user_name": user_data.get("name", "Unknown"),
                "job_title": job_context.get("title", "General") if job_context else "General",
                "filename": file_path.name  # NEW: Include actual filename
            }
            
            if job_id:
                result.update({
                    "job_id": job_id,
                    "pdf_path": str(file_path),
                    "file_path": str(file_path)
                })
            else:
                result["file_path"] = str(file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise ResumeGenerationError(f"Failed to generate resume: {str(e)}")

    
    def _prepare_template_data(
        self, 
        user_data: Dict[str, Any], 
        selected_projects: Optional[List[Dict[str, Any]]] = None,
        job_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Prepare data for template rendering."""
        
        # Default user data structure
        template_data = {
            "name": user_data.get("name", "Firstname Lastname"),
            "phone": user_data.get("phone", "+1(123) 456-7890"),
            "location": user_data.get("location", "San Francisco, CA"),
            "email": user_data.get("email", "contact@example.com"),
            "linkedin_url": user_data.get("linkedin_url", "https://linkedin.com/in/profile"),
            "linkedin_display": user_data.get("linkedin_display", "linkedin.com/in/profile"),
            "website_url": user_data.get("website_url", "www.example.com"),
            "website_display": user_data.get("website_display", "www.example.com"),
            "objective": self._generate_objective(user_data, job_context),
            "education": user_data.get("education", []),
            "skills": user_data.get("skills", []),
            "experience": user_data.get("experience", []),
            "projects": selected_projects or user_data.get("projects", []),
            "extra_curricular": user_data.get("extra_curricular", []),
            "leadership": user_data.get("leadership", [])
        }
        
        return template_data
    
    def _generate_objective(
        self, 
        user_data: Dict[str, Any], 
        job_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate objective statement based on user data and job context."""
        
        experience_years = user_data.get("experience_years", "2+")
        skills = user_data.get("primary_skills", ["Software Development"])
        
        if job_context:
            job_title = job_context.get("title", "Software Engineer")
            # Extract key technologies from job description
            job_skills = job_context.get("requirements", [])[:3]  # Top 3 skills
            skills_text = ", ".join(job_skills) if job_skills else ", ".join(skills)
        else:
            job_title = "Software Engineer"
            skills_text = ", ".join(skills)
        
        return f"Software Engineer with {experience_years} years of experience in {skills_text}, seeking full-time {job_title} roles."
    
    def _generate_with_latex(self, resume_id: str, template_data: Dict[str, Any]) -> Path:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy resume.cls to temp directory
            cls_source = self.template_dir / "resume.cls"
            if cls_source.exists():
                cls_dest = temp_path / "resume.cls"
                shutil.copy2(cls_source, cls_dest)
            
            # Render LaTeX template
            template = self.jinja_env.get_template("resume_template.tex")
            latex_content = template.render(**template_data)
            
            # Write LaTeX file
            tex_file = temp_path / f"resume_{resume_id}.tex"
            tex_file.write_text(latex_content, encoding='utf-8')
            
            # Compile with pdflatex
            try:
                # Run pdflatex twice for proper formatting
                for _ in range(2):
                    result = subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", str(tex_file)],
                        cwd=temp_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0:
                        logger.error(f"pdflatex error: {result.stderr}")
                        raise ResumeGenerationError(f"LaTeX compilation failed: {result.stderr}")
                
                # UPDATED: Generate filename with proper format
                user_name = template_data.get("name", "Unknown").replace(" ", "_").lower()
                if "_" in resume_id:  # If resume_id contains job_id or is formatted
                    pdf_filename = f"{user_name}_{resume_id}.pdf"
                else:
                    pdf_filename = f"resume_{resume_id}.pdf"  # Legacy format
                
                # Move generated PDF to output directory with new name
                pdf_source = temp_path / f"resume_{resume_id}.pdf"
                pdf_dest = self.output_dir / pdf_filename
                
                if pdf_source.exists():
                    shutil.move(str(pdf_source), str(pdf_dest))
                    return pdf_dest
                else:
                    raise ResumeGenerationError("PDF file not generated by LaTeX")
                    
            except subprocess.TimeoutExpired:
                raise ResumeGenerationError("LaTeX compilation timed out")

    
    def _generate_with_fallback(self, resume_id: str, template_data: Dict[str, Any]) -> Path:
        """Generate PDF using fallback methods (ReportLab or WeasyPrint)."""
        
        if REPORTLAB_AVAILABLE:
            return self._generate_with_reportlab(resume_id, template_data)
        elif WEASYPRINT_AVAILABLE:
            return self._generate_with_weasyprint(resume_id, template_data)
        else:
            raise ResumeGenerationError("No PDF generation method available")
    
    def _generate_with_reportlab(self, resume_id: str, template_data: Dict[str, Any]) -> Path:
        """Generate PDF using ReportLab."""
        
        pdf_path = self.output_dir / f"resume_{resume_id}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=0.4*inch,
            leftMargin=0.4*inch,
            topMargin=0.4*inch,
            bottomMargin=0.4*inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=1,  # Center alignment
            textColor=colors.black
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.black,
            borderWidth=1,
            borderColor=colors.black,
            borderPadding=3
        )
        
        normal_style = styles['Normal']
        
        # Build content
        content = []
        
        # Name and contact info
        content.append(Paragraph(template_data['name'].upper(), title_style))
        content.append(Paragraph(f"{template_data['phone']} | {template_data['location']}", normal_style))
        content.append(Paragraph(f"{template_data['email']} | {template_data['linkedin_display']} | {template_data['website_display']}", normal_style))
        content.append(Spacer(1, 12))
        
        # Objective
        content.append(Paragraph("OBJECTIVE", heading_style))
        content.append(Paragraph(template_data['objective'], normal_style))
        content.append(Spacer(1, 12))
        
        # Education
        if template_data['education']:
            content.append(Paragraph("EDUCATION", heading_style))
            for edu in template_data['education']:
                edu_text = f"<b>{edu.get('degree', '')}</b>, {edu.get('institution', '')} - {edu.get('year', '')}"
                content.append(Paragraph(edu_text, normal_style))
                if edu.get('coursework'):
                    content.append(Paragraph(f"Relevant Coursework: {edu['coursework']}", normal_style))
            content.append(Spacer(1, 12))
        
        # Skills
        if template_data['skills']:
            content.append(Paragraph("SKILLS", heading_style))
            for skill_cat in template_data['skills']:
                skill_text = f"<b>{skill_cat.get('category', '')}:</b> {', '.join(skill_cat.get('items', []))}"
                content.append(Paragraph(skill_text, normal_style))
            content.append(Spacer(1, 12))
        
        # Experience
        if template_data['experience']:
            content.append(Paragraph("EXPERIENCE", heading_style))
            for exp in template_data['experience']:
                exp_header = f"<b>{exp.get('role', '')}</b> - {exp.get('duration', '')}<br/>{exp.get('company', '')} | {exp.get('location', '')}"
                content.append(Paragraph(exp_header, normal_style))
                for achievement in exp.get('achievements', []):
                    content.append(Paragraph(f"• {achievement}", normal_style))
                content.append(Spacer(1, 6))
        
        # Projects
        if template_data['projects']:
            content.append(Paragraph("PROJECTS", heading_style))
            for project in template_data['projects']:
                project_text = f"<b>{project.get('title', '')}</b>: {project.get('description', '')}"
                content.append(Paragraph(project_text, normal_style))
            content.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(content)
        
        return pdf_path
    
    def _generate_with_weasyprint(self, resume_id: str, template_data: Dict[str, Any]) -> Path:
        """Generate PDF using WeasyPrint (HTML to PDF)."""
        
        # Create HTML template for WeasyPrint
        html_content = self._create_html_resume(template_data)
        
        pdf_path = self.output_dir / f"resume_{resume_id}.pdf"
        
        # Generate PDF from HTML
        weasyprint.HTML(string=html_content).write_pdf(str(pdf_path))
        
        return pdf_path
    
    def _create_html_resume(self, template_data: Dict[str, Any]) -> str:
        """Create HTML version of resume for WeasyPrint."""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0.4in; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .name {{ font-size: 18px; font-weight: bold; text-transform: uppercase; }}
                .contact {{ margin: 5px 0; }}
                .section {{ margin: 15px 0; }}
                .section-title {{ font-weight: bold; font-size: 12px; text-transform: uppercase; 
                                 border-bottom: 1px solid black; padding-bottom: 2px; margin-bottom: 8px; }}
                .experience-item {{ margin-bottom: 10px; }}
                .experience-header {{ font-weight: bold; }}
                .experience-details {{ font-style: italic; }}
                ul {{ margin: 5px 0; padding-left: 20px; }}
                li {{ margin: 2px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">{template_data['name']}</div>
                <div class="contact">{template_data['phone']} | {template_data['location']}</div>
                <div class="contact">{template_data['email']} | {template_data['linkedin_display']} | {template_data['website_display']}</div>
            </div>
            
            <div class="section">
                <div class="section-title">Objective</div>
                <p>{template_data['objective']}</p>
            </div>
        """
        
        # Add other sections...
        # (This is a simplified version - you can expand it)
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def get_resume_path(self, resume_id: str) -> Optional[Path]:
        """Get the file path for a generated resume."""
        pdf_path = self.output_dir / f"resume_{resume_id}.pdf"
        return pdf_path if pdf_path.exists() else None
    
    def cleanup_old_resumes(self, days_old: int = 7):
        """Clean up resume files older than specified days."""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        for file_path in self.output_dir.glob("resume_*.pdf"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logger.info(f"Cleaned up old resume: {file_path.name}")


# Global instance
resume_generator = ResumeGenerator()