# Contributing to Automated Job Application System

Thank you for your interest in contributing to our AI-powered job application automation system! We welcome contributions from developers of all skill levels.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite
- Redis (optional, for caching)
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/automated-job-application-system.git
   cd automated-job-application-system
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**
   ```bash
   python setup_db.py
   alembic upgrade head
   ```

5. **Run the Application**
   ```bash
   python start_server.py
   ```

6. **Verify Setup**
   - Visit `http://localhost:8000/docs` for API documentation
   - Run `python test_integration_simple.py` to test basic functionality

## 📋 How to Contribute

### Finding Issues to Work On

We use labels to help you find suitable issues:

- 🟢 **`good first issue`** - Perfect for newcomers
- 🟡 **`beginner`** - Requires basic Python/FastAPI knowledge
- 🟠 **`intermediate`** - Involves multiple components or advanced concepts
- 🔴 **`advanced`** - Complex architectural changes

Check our [GitHub Issues](GITHUB_ISSUES.md) for a comprehensive list of available tasks.

### Before You Start

1. **Check existing issues** - Make sure someone isn't already working on it
2. **Comment on the issue** - Let us know you're interested
3. **Ask questions** - We're here to help clarify requirements
4. **Start small** - Begin with good first issues to understand the codebase

## 🔧 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/issue-description
# Examples:
# git checkout -b feature/add-job-filters
# git checkout -b fix/environment-loading
# git checkout -b docs/api-examples
```

### 2. Make Your Changes

#### Code Style Guidelines
- **Follow PEP 8** for Python code formatting
- **Use type hints** for all function parameters and return values
- **Write docstrings** for all public methods and classes
- **Keep functions focused** - one responsibility per function
- **Use meaningful variable names** - avoid abbreviations

#### Example Code Style
```python
from typing import List, Optional
from pydantic import BaseModel

class JobFilter(BaseModel):
    """Filter criteria for job searches."""
    
    location: Optional[str] = None
    salary_min: Optional[int] = None
    remote_only: bool = False

async def search_jobs(
    filters: JobFilter,
    limit: int = 50,
    offset: int = 0
) -> List[Job]:
    """
    Search for jobs based on provided filters.
    
    Args:
        filters: Job search criteria
        limit: Maximum number of results to return
        offset: Number of results to skip
        
    Returns:
        List of matching job objects
        
    Raises:
        ValidationError: If filters are invalid
    """
    # Implementation here
    pass
```

### 3. Testing Your Changes

#### Run Existing Tests
```bash
python -m pytest test_integration_simple.py -v
```

#### Add New Tests
For new features, add tests in the appropriate location:
- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test API endpoints
- **Service tests**: Test business logic

Example test structure:
```python
import pytest
from app.services.job_service import JobService

class TestJobService:
    def test_search_jobs_with_filters(self):
        """Test job search with location filter."""
        # Arrange
        service = JobService()
        filters = {"location": "Remote"}
        
        # Act
        results = service.search_jobs(filters)
        
        # Assert
        assert len(results) > 0
        assert all("remote" in job.location.lower() for job in results)
```

### 4. Documentation

#### Update Documentation When You:
- Add new API endpoints
- Change existing functionality
- Add new configuration options
- Create new services or utilities

#### Documentation Files to Consider:
- `API_DOCUMENTATION.md` - For API changes
- `README.md` - For setup or usage changes
- `DEPLOYMENT_GUIDE.md` - For deployment-related changes
- Inline code comments - For complex logic

### 5. Commit Your Changes

#### Commit Message Format
```
type(scope): brief description

Longer description if needed

Fixes #issue-number
```

#### Commit Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples:
```bash
git commit -m "feat(jobs): add location and salary filters to job search

- Add query parameters for location and salary filtering
- Implement database filtering logic
- Update API documentation with examples

Fixes #6"
```

### 6. Submit a Pull Request

#### Before Submitting:
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

#### Pull Request Template:
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

## Related Issues
Fixes #issue-number
```

## 🏗️ Project Structure

Understanding the codebase structure will help you navigate and contribute effectively:

```
automated-job-application-system/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Configuration and settings
│   ├── database/             # Database setup and utilities
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   └── templates/            # Jinja2 templates
├── alembic/                  # Database migrations
├── static/                   # Static files (CSS, JS, images)
├── tests/                    # Test files
└── docs/                     # Additional documentation
```

### Key Components:

#### Services Layer (`app/services/`)
- **`job_fetcher.py`** - Fetches jobs from external APIs
- **`resume_generator.py`** - Generates resumes in various formats
- **`cover_letter_generator.py`** - AI-powered cover letter generation
- **`job_service.py`** - Job-related business logic

#### API Layer (`app/api/v1/endpoints/`)
- **`jobs.py`** - Job search and management endpoints
- **`resume.py`** - Resume generation endpoints
- **`cover_letters.py`** - Cover letter generation endpoints
- **`project_matching.py`** - ML-based project matching

#### Models (`app/models/`)
- Database table definitions using SQLAlchemy
- Relationships between entities

#### Schemas (`app/schemas/`)
- Request/response validation using Pydantic
- Data serialization and deserialization

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test API endpoints and database interactions
3. **Service Tests** - Test business logic and external integrations

### Writing Good Tests

```python
# Good test example
def test_job_search_filters_location():
    """Test that location filter works correctly."""
    # Arrange - Set up test data
    jobs = [
        Job(title="Remote Developer", location="Remote"),
        Job(title="NYC Developer", location="New York, NY")
    ]
    
    # Act - Perform the action
    filtered_jobs = filter_jobs_by_location(jobs, "Remote")
    
    # Assert - Verify the result
    assert len(filtered_jobs) == 1
    assert filtered_jobs[0].location == "Remote"
```

### Test Data
- Use fixtures for reusable test data
- Mock external API calls
- Use test database for integration tests

## 🔍 Code Review Process

### What We Look For:

1. **Functionality** - Does the code work as intended?
2. **Code Quality** - Is it readable, maintainable, and well-structured?
3. **Testing** - Are there appropriate tests?
4. **Documentation** - Is it properly documented?
5. **Performance** - Are there any performance concerns?
6. **Security** - Are there any security implications?

### Review Timeline:
- Initial review within 2-3 days
- Follow-up reviews within 1-2 days
- We'll provide constructive feedback and suggestions

## 🐛 Reporting Bugs

### Before Reporting:
1. Check if the bug has already been reported
2. Try to reproduce the issue
3. Gather relevant information (logs, environment details)

### Bug Report Template:
```markdown
## Bug Description
Clear description of what went wrong.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should have happened.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Browser (if applicable): [e.g., Chrome 95]

## Additional Context
Any other relevant information, logs, or screenshots.
```

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** your feature would solve
3. **Explain your proposed solution**
4. **Consider alternatives** you've thought about
5. **Provide examples** of how it would work

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Collaborative
- Help others learn and grow
- Share knowledge and resources
- Provide constructive feedback
- Celebrate others' contributions

### Be Patient
- Remember that everyone is learning
- Take time to explain concepts clearly
- Be understanding of different skill levels
- Ask for clarification when needed

## 📞 Getting Help

### Where to Ask Questions:
1. **GitHub Issues** - For bug reports and feature requests
2. **GitHub Discussions** - For general questions and ideas
3. **Code Comments** - For specific implementation questions
4. **Pull Request Reviews** - For code-specific feedback

### What to Include When Asking for Help:
- Clear description of what you're trying to do
- What you've already tried
- Relevant code snippets or error messages
- Your environment details

## 🏆 Recognition

We appreciate all contributions! Contributors will be:
- Listed in our README contributors section
- Mentioned in release notes for significant contributions
- Invited to join our contributor community
- Eligible for special contributor badges

## 📚 Additional Resources

### Learning Resources:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Project-Specific Docs:
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [System Overview](SYSTEM_OVERVIEW.md)
- [Adding Job Sources](ADDING_JOB_SOURCES.md)

---

## 🙏 Thank You!

Thank you for contributing to the Automated Job Application System! Your contributions help make job searching easier and more efficient for everyone.

If you have any questions about contributing, don't hesitate to ask. We're here to help and excited to work with you!

Happy coding! 🚀