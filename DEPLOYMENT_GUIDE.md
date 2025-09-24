# 🚀 Deployment Guide

Complete guide for deploying the Job Application Automation System in production.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   FastAPI App   │    │   PostgreSQL    │
│   (nginx/ALB)   │◄──►│   (Port 8000)   │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │     Redis       │    │   File Storage  │
│   (S3/CDN)      │    │    Cache        │    │   (S3/Local)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM
- 10GB+ disk space

### Quick Start

1. **Clone Repository**
```bash
git clone <repository-url>
cd job-application-system
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section)
```

3. **Deploy with Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services Included
- **FastAPI Backend** (Port 8000)
- **PostgreSQL Database** (Port 5432)
- **Redis Cache** (Port 6379)
- **Nginx Reverse Proxy** (Port 80/443)

## 🔧 Environment Variables

### Required Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database

# Security
SECRET_KEY=your-super-secret-key-min-32-characters

# Application
PROJECT_NAME="Job Application System"
ENVIRONMENT=production
DEBUG=false
```

### Optional API Keys
```bash
# Job Sources (for enhanced functionality)
REED_API_KEY=your-reed-api-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# AI Services (for cover letter generation)
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key

# Caching (for performance)
REDIS_URL=redis://redis:6379/0

# CORS (for frontend integration)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Production Settings
```bash
# Logging
LOG_LEVEL=INFO

# File Storage
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB

# Rate Limiting
API_RATE_LIMIT=100/minute
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and Push Docker Image**
```bash
# Build image
docker build -t job-app-system .

# Tag for ECR
docker tag job-app-system:latest 123456789.dkr.ecr.us-west-2.amazonaws.com/job-app-system:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-west-2.amazonaws.com/job-app-system:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "job-app-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "job-app-system",
      "image": "123456789.dkr.ecr.us-west-2.amazonaws.com/job-app-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/job-app-system",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Required AWS Resources**
- **RDS PostgreSQL** instance
- **ElastiCache Redis** cluster
- **Application Load Balancer**
- **ECS Cluster** with Fargate
- **S3 Bucket** for file storage
- **CloudWatch** for logging

#### Using Lambda (Serverless)

For lighter workloads, deploy as Lambda functions:

```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy --stage production
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and Deploy**
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/job-app-system

# Deploy to Cloud Run
gcloud run deploy job-app-system \
  --image gcr.io/PROJECT_ID/job-app-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://... \
  --memory 1Gi \
  --cpu 1
```

2. **Required GCP Resources**
- **Cloud SQL PostgreSQL** instance
- **Memorystore Redis** instance
- **Cloud Storage** bucket
- **Cloud Load Balancing**

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name job-app-rg --location eastus

# Deploy container
az container create \
  --resource-group job-app-rg \
  --name job-app-system \
  --image your-registry/job-app-system:latest \
  --cpu 1 --memory 2 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL=postgresql://... \
    REDIS_URL=redis://...
```

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Using Let's Encrypt with Nginx**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Security Headers**
```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### Database Security

1. **Connection Security**
```bash
# Use SSL connections
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Restrict database access by IP
# Configure PostgreSQL pg_hba.conf
```

2. **Backup Strategy**
```bash
# Automated daily backups
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Store backups in S3
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

## 📊 Monitoring & Logging

### Application Monitoring

1. **Health Checks**
```bash
# Configure health check endpoint
curl -f http://localhost:8000/health || exit 1
```

2. **Metrics Collection**
```python
# Add to main.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
```

### Log Management

1. **Structured Logging**
```python
# Configure in main.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

2. **Log Aggregation**
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Cloud Solutions**: AWS CloudWatch, GCP Cloud Logging
- **Third-party**: Datadog, New Relic, Sentry

## 🚀 Performance Optimization

### Database Optimization

1. **Connection Pooling**
```python
# Configure in database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

2. **Indexing**
```sql
-- Add indexes for common queries
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date DESC);
```

### Caching Strategy

1. **Redis Configuration**
```bash
# Redis production settings
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

2. **Application Caching**
```python
# Cache frequently accessed data
@lru_cache(maxsize=1000)
def get_job_requirements(job_id: str):
    # Expensive computation
    pass
```

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancing**
```nginx
upstream app_servers {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    location / {
        proxy_pass http://app_servers;
    }
}
```

2. **Database Scaling**
- **Read Replicas**: For read-heavy workloads
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Sharding**: For very large datasets

### Auto-scaling

1. **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: job-app-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: job-app-system
  template:
    spec:
      containers:
      - name: job-app-system
        image: job-app-system:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## 🔧 Maintenance

### Regular Tasks

1. **Database Maintenance**
```bash
# Weekly vacuum and analyze
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# Monitor database size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size('database_name'));"
```

2. **Log Rotation**
```bash
# Configure logrotate
/var/log/job-app-system/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

3. **File Cleanup**
```bash
# Clean old generated files (run daily)
find /app/generated -name "*.pdf" -mtime +7 -delete
find /app/generated -name "*.txt" -mtime +7 -delete
```

### Backup Strategy

1. **Database Backups**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL | gzip > backup_$DATE.sql.gz
aws s3 cp backup_$DATE.sql.gz s3://your-backup-bucket/
```

2. **Application Data**
```bash
# Backup generated files
tar -czf generated_files_$DATE.tar.gz /app/generated/
aws s3 cp generated_files_$DATE.tar.gz s3://your-backup-bucket/
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check connection pool
# Monitor active connections in logs
```

2. **Memory Issues**
```bash
# Monitor memory usage
docker stats

# Check for memory leaks
# Monitor application metrics
```

3. **API Rate Limits**
```bash
# Monitor external API usage
# Implement exponential backoff
# Use caching to reduce API calls
```

### Debug Mode

```bash
# Enable debug mode (development only)
DEBUG=true python start_server_fixed.py

# Check logs
docker-compose logs -f app
```

---

**For additional support, check the troubleshooting section in the main README or create an issue in the repository.**