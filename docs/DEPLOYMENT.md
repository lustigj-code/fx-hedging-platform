# Deployment Guide

## Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/yourorg/fx-hedging-platform.git
cd fx-hedging-platform

# Start with Docker
docker-compose up

# Platform available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Production Deployment

### Option 1: Docker on VPS (Recommended for MVP)

**Providers**: DigitalOcean, Linode, Vultr

**Server Requirements**:
- 2 CPU cores
- 4 GB RAM
- 50 GB SSD
- Ubuntu 22.04 LTS

**Steps**:

1. **Provision Server**
```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y
```

2. **Deploy Application**
```bash
# Clone repository
git clone https://github.com/yourorg/fx-hedging-platform.git
cd fx-hedging-platform

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

3. **Configure HTTPS (Let's Encrypt)**
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

4. **Set Up Nginx Reverse Proxy**
```nginx
# /etc/nginx/sites-available/fx-hedging
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: AWS (Production Scale)

**Services Used**:
- ECS (Fargate) for containers
- RDS (PostgreSQL) for database
- ElastiCache (Redis) for caching
- CloudFront for CDN
- Route 53 for DNS

**Infrastructure as Code** (Terraform example):
```hcl
# main.tf
resource "aws_ecs_cluster" "fx_hedging" {
  name = "fx-hedging-cluster"
}

resource "aws_db_instance" "postgres" {
  engine         = "postgres"
  instance_class = "db.t3.medium"
  allocated_storage = 100
}

# ... (full Terraform config in separate repo)
```

### Option 3: Heroku (Fastest Deployment)

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create apps
heroku create fx-hedging-backend
heroku create fx-hedging-frontend

# Deploy backend
cd backend
git push heroku main

# Deploy frontend
cd ../frontend
git push heroku main

# Configure environment
heroku config:set DATABASE_URL=postgresql://...
heroku config:set EXCHANGERATE_API_KEY=...
```

## Database Migration (SQLite → PostgreSQL)

```bash
# Export from SQLite
sqlite3 fx_hedging.db .dump > backup.sql

# Update .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fx_hedging

# Run migrations
cd backend
alembic upgrade head

# Import data (manual)
# Convert SQL if needed
```

## Environment Variables (Production)

```bash
# Application
APP_NAME="FX Hedging Platform"
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://user:password@db.example.com:5432/fx_hedging

# APIs
EXCHANGERATE_API_KEY=production_key_here

# Security
SECRET_KEY=generate_random_256_bit_key

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Monitoring

### Application Monitoring (Sentry)

```bash
pip install sentry-sdk

# In main.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Server Monitoring

- **Uptime**: UptimeRobot (free)
- **Logs**: Papertrail, Loggly
- **Metrics**: Prometheus + Grafana

## Backup Strategy

```bash
# Daily database backup
0 2 * * * docker exec postgres pg_dump -U user fx_hedging > /backups/db_$(date +\%Y\%m\%d).sql

# Weekly full backup
0 3 * * 0 tar -czf /backups/full_$(date +\%Y\%m\%d).tar.gz /var/www/fx-hedging

# Upload to S3
aws s3 cp /backups/ s3://your-backup-bucket/ --recursive
```

## Security Checklist

- [ ] HTTPS enabled (SSL/TLS)
- [ ] Environment variables secured
- [ ] Database encrypted
- [ ] API keys rotated
- [ ] Rate limiting configured
- [ ] Firewall rules set
- [ ] Regular security audits

## Scaling

**Horizontal Scaling**:
- Load balancer (Nginx, HAProxy, or AWS ALB)
- Multiple backend containers
- Redis for session storage

**Vertical Scaling**:
- Increase server resources as needed
- Monitor CPU/RAM usage

## Troubleshooting

**502 Bad Gateway**: Check if backend container is running
**Database Connection Error**: Verify DATABASE_URL
**CORS Errors**: Check CORS_ORIGINS in .env

## Support

Deployment assistance: ops@fxhedging.com
