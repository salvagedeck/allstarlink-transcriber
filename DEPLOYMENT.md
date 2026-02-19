# Deployment Guide

Production-ready deployment instructions for AllStarLink Transcriber.

## Pre-Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] Access to AllStarLink node confirmed
- [ ] Port 8000 available (or configured alternative)
- [ ] At least 4GB RAM available
- [ ] 2GB disk space for database and logs
- [ ] Network connectivity to AllStarLink node verified

## Local Deployment (Development)

```bash
# Clone and setup
git clone <repo-url> allstarlink-transcriber
cd allstarlink-transcriber
cp .env.example .env

# Edit configuration
nano .env

# Build and run
docker-compose build
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:8000/api/status
```

## Server Deployment (Production)

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

### 2. Clone Repository

```bash
cd /opt
sudo git clone <repo-url> allstarlink-transcriber
cd allstarlink-transcriber
```

### 3. Configure Environment

```bash
sudo cp .env.example .env
sudo nano .env

# Set your values:
# ALLSTARLINK_NODE=9001
# ALLSTARLINK_HOST=<node-ip>
# ALLSTARLINK_USER=<username>
# ALLSTARLINK_PASSWORD=<password>
# UI_THEME=dark
```

### 4. Build and Deploy

```bash
# Build the Docker image
sudo docker-compose build --no-cache

# Start service
sudo docker-compose up -d

# Verify startup
sudo docker-compose logs -f
```

### 5. Post-Deployment Verification

```bash
# Check service status
sudo docker-compose ps

# Test API endpoint
curl http://localhost:8000/api/status

# Check logs for errors
sudo docker-compose logs | grep -i error

# Verify database created
sudo docker-compose exec allstarlink-transcriber \
  test -f /app/data/transcripts.db && echo "Database OK" || echo "Database missing"
```

## Nginx Reverse Proxy (Optional)

For production with SSL, use Nginx as reverse proxy.

### 1. Install Nginx

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/allstarlink-transcriber`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Backend proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 3600;
    }
}
```

Enable and test:

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/allstarlink-transcriber \
    /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Get SSL certificate
sudo certbot certonly --nginx -d your-domain.com

# Enable site
sudo systemctl restart nginx
```

## Docker Hub Deployment

Push image to Docker Hub for easy deployment:

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag allstarlink-transcriber:latest \
    yourusername/allstarlink-transcriber:latest

# Push
docker push yourusername/allstarlink-transcriber:latest

# Deploy elsewhere
docker run -d \
    --name allstarlink-transcriber \
    -p 8000:8000 \
    --env-file .env \
    -v transcripts_data:/app/data \
    yourusername/allstarlink-transcriber:latest
```

## Monitoring

### System Monitoring

```bash
# Monitor resource usage
docker stats allstarlink-transcriber

# View detailed logs
docker-compose logs -f --tail=100

# Check health
docker-compose exec allstarlink-transcriber \
    curl -f http://localhost:8000/api/status || echo "Unhealthy"
```

### Log Rotation

Configure log rotation in `/etc/logrotate.d/allstarlink-transcriber`:

```
/var/lib/docker/containers/**/allstarlink-transcriber*-json.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    copytruncate
}
```

## Database Maintenance

### Backup Transcripts

```bash
# Backup database
docker-compose exec allstarlink-transcriber \
    tar czf /tmp/transcripts_backup.tar.gz /app/data/

# Copy to host
docker cp allstarlink-transcriber:/tmp/transcripts_backup.tar.gz ./

# Or export as CSV
docker-compose exec allstarlink-transcriber \
    sqlite3 /app/data/transcripts.db \
    ".mode csv" \
    ".output /tmp/transcripts.csv" \
    "SELECT * FROM transcripts;"
```

### Database Maintenance

```bash
# Run SQLite VACUUM to optimize
docker-compose exec allstarlink-transcriber \
    sqlite3 /app/data/transcripts.db "VACUUM;"

# Check database integrity
docker-compose exec allstarlink-transcriber \
    sqlite3 /app/data/transcripts.db "PRAGMA integrity_check;"
```

## Updates

### Update Container

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker-compose build --no-cache

# Restart service
docker-compose up -d

# Verify
docker-compose logs -f
```

## Troubleshooting

### Service crashes immediately

```bash
# Check logs
docker-compose logs

# Common issues:
# - Whisper model download failed (needs ~500MB)
# - iaxclient installation failed
# - Insufficient disk space
```

### High CPU usage

```bash
# Reduce model size
WHISPER_MODEL=tiny

# Or increase chunk size
AUDIO_CHUNK_SECONDS=30

# Monitor per-component usage
docker stats
```

### Database getting too large

```bash
# Delete old transcripts
docker-compose exec allstarlink-transcriber \
    sqlite3 /app/data/transcripts.db \
    "DELETE FROM transcripts WHERE datetime(created_at) < datetime('now', '-30 days');"
```

## Security Hardening

### Network Security

```yaml
# In docker-compose.yml
services:
  allstarlink-transcriber:
    # Only expose to localhost if using reverse proxy
    ports:
      - "127.0.0.1:8000:8000"  # Local only
    
    # Or use internal network
    networks:
      - internal
    
networks:
  internal:
    driver: bridge
```

### Data Security

```bash
# Set proper file permissions
sudo chown -R root:docker /opt/allstarlink-transcriber
sudo chmod -R 750 /opt/allstarlink-transcriber

# Protect .env
sudo chmod 600 /opt/allstarlink-transcriber/.env
```

## Support

For deployment issues:
1. Check [README.md](README.md) for configuration options
2. Review logs: `docker-compose logs -f`
3. Test connectivity to AllStarLink node
4. Ensure sufficient system resources

---

**Production Deployment v1.0.0**
