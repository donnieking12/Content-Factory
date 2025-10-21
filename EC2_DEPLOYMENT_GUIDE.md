# AWS EC2 Deployment Guide - Content Factory

## 🚀 Deploy to AWS EC2

**EC2 Instance:** `ec2-13-36-168-66.eu-west-3.compute.amazonaws.com`  
**Region:** EU West 3 (Paris)

---

## ✅ Pre-Deployment Checklist

### 1. EC2 Instance Requirements
- **OS:** Ubuntu 22.04 LTS (recommended)
- **Instance Type:** t2.medium or larger (2 vCPU, 4GB RAM minimum)
- **Storage:** 20GB+ SSD
- **Security Group:** 
  - Port 22 (SSH)
  - Port 80 (HTTP)
  - Port 443 (HTTPS)
  - Port 8000 (Application - optional, for testing)

### 2. Domain Configuration
Your EC2 instance is accessible at:
- **Public DNS:** `ec2-13-36-168-66.eu-west-3.compute.amazonaws.com`
- **IP Address:** `13.36.168.66`

---

## 📋 Deployment Steps

### Step 1: Connect to EC2 Instance

```bash
# Replace with your key file path
ssh -i "your-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
```

### Step 2: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Logout and login again for group changes
exit
```

### Step 3: Prepare Production Environment

```bash
# Reconnect to EC2
ssh -i "your-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com

# Create application directory
mkdir -p ~/content-factory
cd ~/content-factory
```

### Step 4: Transfer Files to EC2

**From your local machine:**

```bash
# Navigate to project directory
cd c:\Users\HP\Desktop\Donnie\Content-Factory

# Option 1: Using SCP (from Windows, use Git Bash or WSL)
scp -i "your-key.pem" -r . ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:~/content-factory/

# Option 2: Using Git (recommended)
# First, push to GitHub
git add .
git commit -m "Production deployment"
git push origin main

# Then on EC2:
git clone https://github.com/your-username/content-factory.git ~/content-factory
cd ~/content-factory
```

### Step 5: Configure Production Environment

**On EC2:**

```bash
cd ~/content-factory

# Create production .env file
nano .env
```

**Production `.env` configuration:**

```env
# AI Content Factory Environment Variables - PRODUCTION
# ==============================================

# Database settings (Supabase)
SUPABASE_URL=https://qcmmqmqerjyfvftdlttv.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjbW1xbXFlcmp5ZnZmdGRsdHR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDQ1MTgsImV4cCI6MjA3Mzc4MDUxOH0.7s_vzE9UU0JcZdLhBhWbOV5eDV66s6A1-pzvVo3xIGo
SUPABASE_DB_PASSWORD=Donnieking1290@

# Redis settings for Celery
REDIS_URL=redis://redis:6379/0

# Social media API keys
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
INSTAGRAM_PAGE_ID=your_instagram_page_id
YOUTUBE_API_KEY=your_youtube_api_key

# YouTube OAuth settings
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
YOUTUBE_CLIENT_SECRET_FILE=google_client_secret.json

# AI Service API keys
OPENAI_API_KEY=your_openai_api_key_here

# AI Avatar service settings
AI_AVATAR_API_URL=your_ai_avatar_api_url
AI_AVATAR_API_KEY=your_ai_avatar_api_key

# FFmpeg path
FFMPEG_PATH=ffmpeg

# Environment
ENVIRONMENT=production

# Application Base URL (for OAuth redirects)
APP_BASE_URL=http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000

# Security settings
SECRET_KEY=your_production_secret_key_change_this_to_random_string_32_chars_min
```

Save and exit (Ctrl+X, Y, Enter)

### Step 6: Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f app
```

### Step 7: Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# From your local machine
curl http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health
```

---

## 🔐 Google OAuth Configuration Update

### Important: Update Google Cloud Console

You need to add the EC2 URL to your Google OAuth authorized redirect URIs:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: `ai-content-prod`
3. Navigate to: APIs & Services → Credentials
4. Click on your OAuth 2.0 Client ID: `143119762023-gphmghekf50hmb8lbh3s1uj6lctl6gha`
5. Under "Authorized redirect URIs", add:
   ```
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/oauth2callback
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com/api/v1/social-media/youtube/oauth2callback
   ```
6. Under "Authorized JavaScript origins", add:
   ```
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
   ```
7. Click "Save"

**Note:** The `google_client_secret.json` file has been pre-configured with these URIs.

---

## 🌐 Accessing Your Application

### API Endpoints
- **Root:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/
- **Health:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health
- **API Docs:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/docs
- **Products:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/products/
- **Videos:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/videos/

### YouTube OAuth
1. **Auth Status:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth-status
2. **Start Auth:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth

---

## 🔧 Production Configuration

### Docker Compose Services

Your production deployment includes:

1. **app** - FastAPI application (Port 8000)
2. **redis** - Message broker for Celery
3. **celery_worker** - Background task processor
4. **celery_beat** - Task scheduler

### Useful Commands

```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart a service
docker-compose -f docker-compose.prod.yml restart app

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Execute commands in container
docker-compose -f docker-compose.prod.yml exec app python -c "from app.core.config import settings; print(settings.SUPABASE_URL)"
```

---

## 📊 Monitoring

### Application Logs
```bash
# Real-time logs
docker-compose -f docker-compose.prod.yml logs -f app

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 app
```

### System Resources
```bash
# Monitor container stats
docker stats

# Check disk usage
df -h

# Check memory
free -h
```

---

## 🔒 Security Best Practices

### 1. Firewall Configuration
```bash
# Install UFW
sudo apt install ufw

# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow application port (optional, for testing)
sudo ufw allow 8000

# Enable firewall
sudo ufw enable
```

### 2. SSL/TLS Certificate (Optional - Recommended)

For HTTPS, use Let's Encrypt with Nginx:

```bash
# Install Nginx
sudo apt install nginx

# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (if you have a domain)
sudo certbot --nginx -d yourdomain.com
```

### 3. Environment Security
- ✅ Keep `.env` file secure (never commit to git)
- ✅ Use strong `SECRET_KEY`
- ✅ Restrict security group to known IPs
- ✅ Regular system updates

---

## 🚨 Troubleshooting

### Application won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs app

# Check container status
docker ps -a

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Can't connect from outside
```bash
# Check if app is listening
sudo netstat -tlnp | grep 8000

# Check security group in AWS Console
# Ensure port 8000 is open
```

### Database connection issues
```bash
# Test Supabase connection
docker-compose -f docker-compose.prod.yml exec app python -c "from supabase import create_client; from app.core.config import settings; client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY); print('Connected!')"
```

### YouTube OAuth not working
1. Verify redirect URIs in Google Cloud Console
2. Check `APP_BASE_URL` in `.env`
3. Ensure `google_client_secret.json` is uploaded
4. Check firewall allows incoming connections

---

## 📈 Scaling & Performance

### Increase Worker Processes

Edit `docker-compose.prod.yml`:

```yaml
app:
  command: gunicorn app.main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Add More Celery Workers

```yaml
celery_worker_2:
  build:
    context: .
    dockerfile: Dockerfile.prod
  command: celery -A celery_worker.celery_app worker --loglevel=info
  env_file:
    - .env
  depends_on:
    - redis
```

### Use Larger Instance
- **For high load:** t2.large or t2.xlarge
- **For production:** t3.medium or c5.large

---

## 🎯 Next Steps

1. ✅ **Verify Deployment** - Test all endpoints
2. ✅ **Configure SSL** - Set up HTTPS with custom domain
3. ✅ **Set up monitoring** - Use CloudWatch or similar
4. ✅ **Configure backups** - Automated Supabase backups
5. ✅ **Load testing** - Test with expected traffic
6. ✅ **CI/CD Pipeline** - Automate deployments with GitHub Actions

---

## 📞 Support Resources

- **AWS EC2 Documentation:** https://docs.aws.amazon.com/ec2/
- **Docker Documentation:** https://docs.docker.com/
- **Application Logs:** `docker-compose logs -f`
- **Health Check:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health

---

## ✅ Deployment Checklist

- [ ] EC2 instance created and accessible
- [ ] Docker and Docker Compose installed
- [ ] Project files transferred
- [ ] `.env` file configured with production values
- [ ] `google_client_secret.json` uploaded
- [ ] Google OAuth redirect URIs updated
- [ ] Docker containers running
- [ ] Health check passing
- [ ] YouTube OAuth tested
- [ ] Firewall configured
- [ ] SSL certificate installed (optional)
- [ ] Monitoring set up
- [ ] Backup strategy in place

---

**Your Content Factory is ready for production on AWS EC2!** 🚀

**Access your application at:**  
http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000
