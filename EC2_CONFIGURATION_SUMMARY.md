# AWS EC2 Deployment - Configuration Summary

## ✅ Configuration Complete!

Your Content Factory application is now configured for deployment to AWS EC2.

---

## 🌐 **EC2 Instance Details**

- **Public DNS:** `ec2-13-36-168-66.eu-west-3.compute.amazonaws.com`
- **IP Address:** `13.36.168.66`
- **Region:** EU West 3 (Paris)
- **Application URL:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000

---

## 📝 **What Was Configured**

### 1. **Google OAuth Redirect URIs Updated** ✅

**File:** `google_client_secret.json`

Added EC2 URLs to authorized redirect URIs:
```json
"redirect_uris": [
  "http://localhost:8000/api/v1/social-media/youtube/oauth2callback",
  "http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com/api/v1/social-media/youtube/oauth2callback",
  "http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/oauth2callback"
],
"javascript_origins": [
  "http://localhost:8000",
  "http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com",
  "http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000"
]
```

### 2. **YouTube OAuth Service Enhanced** ✅

**File:** `app/services/youtube_oauth.py`

- Dynamic redirect URI detection based on environment
- Supports `APP_BASE_URL` environment variable
- Auto-configures for localhost or production URLs

### 3. **Deployment Documentation Created** ✅

**Files:**
- [`EC2_DEPLOYMENT_GUIDE.md`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/EC2_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [`deploy-ec2.sh`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/deploy-ec2.sh) - Automated deployment script
- [`EC2_CONFIGURATION_SUMMARY.md`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/EC2_CONFIGURATION_SUMMARY.md) - This file

---

## 🚀 **Quick Deployment Guide**

### Option 1: Automated Deployment (Recommended)

**On your EC2 instance:**

```bash
# 1. Clone or upload project
git clone <your-repo> ~/content-factory
cd ~/content-factory

# 2. Run deployment script
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

The script automatically:
- ✅ Checks Docker installation
- ✅ Verifies configuration files
- ✅ Builds production containers
- ✅ Starts all services
- ✅ Runs health checks
- ✅ Displays access URLs

### Option 2: Manual Deployment

**On your EC2 instance:**

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 2. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Transfer project files
# (Upload via SCP or git clone)

# 4. Configure environment
cd ~/content-factory
nano .env
# Add: APP_BASE_URL=http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000

# 5. Deploy
docker-compose -f docker-compose.prod.yml up -d --build

# 6. Check health
curl http://localhost:8000/health
```

---

## 🔐 **IMPORTANT: Google Cloud Console Update Required**

After deploying, you **MUST** update your Google OAuth settings:

### Steps:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: **`ai-content-prod`**
3. Navigate to: **APIs & Services → Credentials**
4. Click on OAuth 2.0 Client ID: **`143119762023-gphmghekf50hmb8lbh3s1uj6lctl6gha`**
5. Under "**Authorized redirect URIs**", add:
   ```
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/oauth2callback
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com/api/v1/social-media/youtube/oauth2callback
   ```
6. Under "**Authorized JavaScript origins**", add:
   ```
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
   ```
7. Click **"Save"**

**Note:** These URLs are pre-configured in `google_client_secret.json`, but you must also add them in Google Cloud Console for OAuth to work.

---

## 🌐 **Access URLs**

Once deployed, your application will be accessible at:

### Main Endpoints
- **Root:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/
- **Health Check:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health
- **API Documentation:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/docs

### API Endpoints
- **Products:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/products/
- **Videos:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/videos/
- **Social Media:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/
- **Analytics:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/analytics/
- **Monitoring:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/monitoring/

### YouTube OAuth
- **Auth Status:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth-status
- **Start Authentication:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth
- **Upload Video:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/upload

---

## 📋 **Environment Variables for Production**

Add these to your `.env` file on EC2:

```env
# Application Base URL (REQUIRED for OAuth)
APP_BASE_URL=http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000

# Environment
ENVIRONMENT=production

# Database (Supabase)
SUPABASE_URL=https://qcmmqmqerjyfvftdlttv.supabase.co
SUPABASE_KEY=<your-supabase-key>
SUPABASE_DB_PASSWORD=<your-password>

# OpenAI
OPENAI_API_KEY=<your-openai-key>

# YouTube OAuth
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
YOUTUBE_CLIENT_SECRET_FILE=google_client_secret.json

# Redis (for Docker Compose)
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<generate-strong-random-key>
```

---

## 🔧 **Production Services**

Your Docker Compose deployment includes:

| Service | Description | Port |
|---------|-------------|------|
| **app** | FastAPI application | 8000 |
| **redis** | Message broker | 6379 (internal) |
| **celery_worker** | Background tasks | - |
| **celery_beat** | Scheduled tasks | - |

---

## 🛠️ **Useful Commands**

### On EC2 Instance:

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f app

# Restart application
docker-compose -f docker-compose.prod.yml restart app

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Execute command in container
docker-compose -f docker-compose.prod.yml exec app python manage.py <command>
```

---

## 🔒 **Security Checklist**

- [ ] Configure AWS Security Group (ports 22, 80, 443, 8000)
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Keep `.env` file secure (never commit to git)
- [ ] Update Google OAuth redirect URIs in Cloud Console
- [ ] Enable UFW firewall on EC2
- [ ] Set up SSL certificate (optional but recommended)
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

---

## 📊 **Testing the Deployment**

### From Your Local Machine:

```bash
# Health check
curl http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health

# Get products
curl http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/products/

# Check YouTube auth status
curl http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth-status
```

### Test YouTube OAuth Flow:

1. Visit: http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth
2. Click the provided `auth_url`
3. Authenticate with Google
4. You'll be redirected back to your EC2 instance
5. Check auth status again to verify

---

## 🚨 **Troubleshooting**

### Issue: Can't connect to EC2 instance
**Solution:** 
- Check AWS Security Group allows port 8000
- Verify EC2 instance is running
- Check that Docker containers are up: `docker ps`

### Issue: YouTube OAuth fails
**Solution:**
- Verify redirect URIs in Google Cloud Console
- Check `APP_BASE_URL` in `.env` matches your EC2 URL
- Ensure `google_client_secret.json` is uploaded to EC2

### Issue: Database connection fails
**Solution:**
- Verify Supabase credentials in `.env`
- Check network connectivity from EC2 to Supabase

### Issue: Docker containers won't start
**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Rebuild
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate
```

---

## 📈 **Next Steps**

### Immediate:
1. ✅ Deploy to EC2 using deployment guide
2. ✅ Update Google OAuth settings
3. ✅ Test YouTube authentication
4. ✅ Verify all endpoints work

### Optional Enhancements:
1. **Custom Domain:** Point a domain to EC2 IP (13.36.168.66)
2. **SSL Certificate:** Use Let's Encrypt for HTTPS
3. **Load Balancer:** Set up AWS ELB for high availability
4. **Auto Scaling:** Configure EC2 Auto Scaling Group
5. **Monitoring:** Set up CloudWatch alarms
6. **Backups:** Automated database backups
7. **CI/CD:** GitHub Actions for automated deployments

---

## 📚 **Documentation**

- **Deployment Guide:** [`EC2_DEPLOYMENT_GUIDE.md`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/EC2_DEPLOYMENT_GUIDE.md)
- **YouTube OAuth:** [`YOUTUBE_OAUTH_SETUP.md`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/YOUTUBE_OAUTH_SETUP.md)
- **Project Status:** [`CURRENT_STATUS_REPORT.md`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/CURRENT_STATUS_REPORT.md)
- **Main README:** [`README.md`](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/README.md)

---

## ✅ **Summary**

Your Content Factory application is now **fully configured for AWS EC2 deployment**!

### Configured:
✅ Google OAuth redirect URIs for EC2  
✅ Dynamic base URL detection  
✅ Production environment settings  
✅ Deployment automation scripts  
✅ Comprehensive documentation  

### Ready to Deploy:
- All services containerized
- Production environment configured
- YouTube OAuth EC2-ready
- Automated deployment script available

### Application URLs (after deployment):
- **Main App:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000
- **API Docs:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/docs
- **YouTube OAuth:** http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth

---

**You're ready to deploy to production!** 🚀

Follow the **[EC2_DEPLOYMENT_GUIDE.md](file:///c:/Users/HP/Desktop/Donnie/Content-Factory/EC2_DEPLOYMENT_GUIDE.md)** for step-by-step deployment instructions.
