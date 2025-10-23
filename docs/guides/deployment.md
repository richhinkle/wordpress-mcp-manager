# Deployment Guide

## Overview

This guide covers deploying the Instagram-to-WordPress Manager to various production environments.

## Prerequisites

- Python 3.8+ runtime environment
- WordPress site with AIWU MCP plugin installed
- Apify API account (optional but recommended)
- Domain name and SSL certificate (recommended)

## Environment Configuration

### Production Environment Variables

Create a production `.env` file:

```bash
# WordPress MCP Configuration
WORDPRESS_URL=https://your-site.com/wp-json/mcp/v1/sse
ACCESS_TOKEN=your-production-mcp-token

# Apify Integration
APIFY_API_TOKEN=your-apify-token

# Flask Production Settings
SECRET_KEY=your-secure-random-secret-key
DEBUG=false
PORT=5000

# Cache Configuration
APIFY_CACHE_TTL=7200  # 2 hours for production

# Security Settings
FLASK_ENV=production
```

### Security Considerations

1. **Generate secure secret key**:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **Use environment-specific tokens**:
   - Separate MCP tokens for development/production
   - Rotate tokens regularly
   - Store tokens securely (never in code)

3. **Enable HTTPS**:
   - Use SSL certificates
   - Redirect HTTP to HTTPS
   - Set secure cookie flags

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p cache/apify

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  wordpress-mcp-manager:
    build: .
    ports:
      - "5000:5000"
    environment:
      - WORDPRESS_URL=${WORDPRESS_URL}
      - ACCESS_TOKEN=${ACCESS_TOKEN}
      - APIFY_API_TOKEN=${APIFY_API_TOKEN}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    volumes:
      - ./cache:/app/cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - wordpress-mcp-manager
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t wordpress-mcp-manager .

# Run with environment file
docker run -d \
  --name wp-mcp-manager \
  --env-file .env \
  -p 5000:5000 \
  -v $(pwd)/cache:/app/cache \
  wordpress-mcp-manager

# Or use docker-compose
docker-compose up -d
```

## Cloud Platform Deployments

### Heroku

1. **Prepare application**:
   ```bash
   # Create Procfile
   echo "web: gunicorn --bind 0.0.0.0:\$PORT app:app" > Procfile
   
   # Create runtime.txt
   echo "python-3.9.18" > runtime.txt
   ```

2. **Deploy to Heroku**:
   ```bash
   # Install Heroku CLI and login
   heroku login
   
   # Create app
   heroku create your-wp-manager
   
   # Set environment variables
   heroku config:set WORDPRESS_URL="https://your-site.com/wp-json/mcp/v1/sse"
   heroku config:set ACCESS_TOKEN="your-token"
   heroku config:set APIFY_API_TOKEN="your-apify-token"
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG="false"
   
   # Deploy
   git push heroku main
   ```

3. **Configure add-ons** (optional):
   ```bash
   # Redis for caching
   heroku addons:create heroku-redis:hobby-dev
   
   # Monitoring
   heroku addons:create papertrail:choklad
   ```

### AWS Elastic Beanstalk

1. **Create application package**:
   ```bash
   # Create .ebextensions directory
   mkdir .ebextensions
   ```

2. **Configure environment** (`.ebextensions/python.config`):
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: app:app
     aws:elasticbeanstalk:application:environment:
       PYTHONPATH: "/var/app/current:$PYTHONPATH"
   ```

3. **Deploy**:
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize
   eb init
   
   # Create environment
   eb create production
   
   # Set environment variables
   eb setenv WORDPRESS_URL="https://your-site.com/wp-json/mcp/v1/sse"
   eb setenv ACCESS_TOKEN="your-token"
   eb setenv SECRET_KEY="your-secret-key"
   
   # Deploy
   eb deploy
   ```

### Google Cloud Platform

1. **Create app.yaml**:
   ```yaml
   runtime: python39
   
   env_variables:
     WORDPRESS_URL: "https://your-site.com/wp-json/mcp/v1/sse"
     ACCESS_TOKEN: "your-token"
     APIFY_API_TOKEN: "your-apify-token"
     SECRET_KEY: "your-secret-key"
     DEBUG: "false"
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

2. **Deploy**:
   ```bash
   # Install Google Cloud SDK
   gcloud init
   
   # Deploy
   gcloud app deploy
   ```

### DigitalOcean App Platform

1. **Create app spec** (`.do/app.yaml`):
   ```yaml
   name: wordpress-mcp-manager
   services:
   - name: web
     source_dir: /
     github:
       repo: your-username/wordpress-mcp-manager
       branch: main
     run_command: gunicorn --bind 0.0.0.0:8080 app:app
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: WORDPRESS_URL
       value: "https://your-site.com/wp-json/mcp/v1/sse"
     - key: ACCESS_TOKEN
       value: "your-token"
       type: SECRET
     - key: SECRET_KEY
       value: "your-secret-key"
       type: SECRET
   ```

2. **Deploy via CLI**:
   ```bash
   # Install doctl
   doctl apps create .do/app.yaml
   ```

## Traditional Server Deployment

### Ubuntu/Debian Server

1. **Install dependencies**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and tools
   sudo apt install python3 python3-pip python3-venv nginx supervisor -y
   ```

2. **Setup application**:
   ```bash
   # Create app directory
   sudo mkdir -p /var/www/wordpress-mcp-manager
   cd /var/www/wordpress-mcp-manager
   
   # Clone repository
   sudo git clone https://github.com/your-repo/wordpress-mcp-manager.git .
   
   # Create virtual environment
   sudo python3 -m venv venv
   sudo venv/bin/pip install -r requirements.txt
   
   # Set permissions
   sudo chown -R www-data:www-data /var/www/wordpress-mcp-manager
   ```

3. **Configure Supervisor** (`/etc/supervisor/conf.d/wordpress-mcp-manager.conf`):
   ```ini
   [program:wordpress-mcp-manager]
   command=/var/www/wordpress-mcp-manager/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 app:app
   directory=/var/www/wordpress-mcp-manager
   user=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/wordpress-mcp-manager.log
   environment=WORDPRESS_URL="https://your-site.com/wp-json/mcp/v1/sse",ACCESS_TOKEN="your-token",SECRET_KEY="your-secret-key"
   ```

4. **Configure Nginx** (`/etc/nginx/sites-available/wordpress-mcp-manager`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /static {
           alias /var/www/wordpress-mcp-manager/static;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

5. **Enable and start services**:
   ```bash
   # Enable Nginx site
   sudo ln -s /etc/nginx/sites-available/wordpress-mcp-manager /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   
   # Start Supervisor
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start wordpress-mcp-manager
   ```

### SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Maintenance

### Health Monitoring

1. **Application health endpoint**:
   ```bash
   curl https://your-domain.com/api/health
   ```

2. **Uptime monitoring**:
   - Use services like UptimeRobot, Pingdom, or StatusCake
   - Monitor `/api/health` endpoint
   - Set up alerts for downtime

3. **Log monitoring**:
   ```bash
   # Application logs
   tail -f /var/log/wordpress-mcp-manager.log
   
   # Nginx logs
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

### Performance Optimization

1. **Enable caching**:
   - Use Redis for session storage
   - Implement application-level caching
   - Configure CDN for static assets

2. **Database optimization**:
   - Monitor WordPress database performance
   - Optimize MCP plugin queries
   - Use database caching

3. **Resource monitoring**:
   ```bash
   # Monitor system resources
   htop
   df -h
   free -m
   ```

### Backup Strategy

1. **Application backup**:
   ```bash
   # Backup application files
   tar -czf backup-$(date +%Y%m%d).tar.gz /var/www/wordpress-mcp-manager
   
   # Backup cache data
   tar -czf cache-backup-$(date +%Y%m%d).tar.gz /var/www/wordpress-mcp-manager/cache
   ```

2. **Environment backup**:
   ```bash
   # Backup environment configuration
   cp .env .env.backup-$(date +%Y%m%d)
   ```

3. **Automated backups**:
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup-script.sh
   ```

### Security Hardening

1. **Firewall configuration**:
   ```bash
   # UFW firewall
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. **Regular updates**:
   ```bash
   # System updates
   sudo apt update && sudo apt upgrade -y
   
   # Python dependencies
   pip install --upgrade -r requirements.txt
   ```

3. **Security headers** (add to Nginx config):
   ```nginx
   add_header X-Frame-Options "SAMEORIGIN" always;
   add_header X-XSS-Protection "1; mode=block" always;
   add_header X-Content-Type-Options "nosniff" always;
   add_header Referrer-Policy "no-referrer-when-downgrade" always;
   add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
   ```

## Scaling Considerations

### Horizontal Scaling

1. **Load balancer setup**:
   ```nginx
   upstream app_servers {
       server 127.0.0.1:5000;
       server 127.0.0.1:5001;
       server 127.0.0.1:5002;
   }
   
   server {
       location / {
           proxy_pass http://app_servers;
       }
   }
   ```

2. **Shared cache storage**:
   - Use Redis for shared caching
   - Implement distributed file storage
   - Consider database-backed cache

### Vertical Scaling

1. **Increase server resources**:
   - More CPU cores for concurrent requests
   - Additional RAM for caching
   - Faster storage for cache operations

2. **Optimize application**:
   - Increase Gunicorn workers
   - Tune cache settings
   - Optimize database queries

## Troubleshooting Deployment Issues

### Common Problems

1. **Port binding issues**:
   ```bash
   # Check port usage
   sudo netstat -tlnp | grep :5000
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

2. **Permission errors**:
   ```bash
   # Fix file permissions
   sudo chown -R www-data:www-data /var/www/wordpress-mcp-manager
   sudo chmod -R 755 /var/www/wordpress-mcp-manager
   ```

3. **Environment variable issues**:
   ```bash
   # Check environment in Supervisor
   sudo supervisorctl status
   sudo supervisorctl tail wordpress-mcp-manager
   ```

4. **SSL certificate problems**:
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew if needed
   sudo certbot renew --dry-run
   ```

### Rollback Strategy

1. **Keep previous version**:
   ```bash
   # Before deployment
   cp -r /var/www/wordpress-mcp-manager /var/www/wordpress-mcp-manager.backup
   ```

2. **Quick rollback**:
   ```bash
   # Stop current version
   sudo supervisorctl stop wordpress-mcp-manager
   
   # Restore backup
   rm -rf /var/www/wordpress-mcp-manager
   mv /var/www/wordpress-mcp-manager.backup /var/www/wordpress-mcp-manager
   
   # Restart
   sudo supervisorctl start wordpress-mcp-manager
   ```

This deployment guide provides comprehensive instructions for deploying the Instagram-to-WordPress Manager in various production environments, from simple cloud platforms to complex server setups.