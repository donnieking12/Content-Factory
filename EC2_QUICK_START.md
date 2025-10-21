# EC2 Quick Start Guide - Content Factory

## 🚀 Deploy to Your EC2 Instance

Your EC2 instance: **ec2-13-36-168-66.eu-west-3.compute.amazonaws.com**  
SSH Key: **C:\Users\HP\Desktop\Donnie\aws-factory-key.pem**

---

## ⚡ Quick Deployment (Windows)

### Option 1: Automated Deployment (Recommended)

**Simply double-click:**
```
deploy-to-ec2.bat
```

This will automatically:
1. ✅ Test SSH connection
2. ✅ Transfer all project files
3. ✅ Install Docker & dependencies
4. ✅ Configure environment
5. ✅ Start the application
6. ✅ Run health checks

---

### Option 2: Manual SSH Connection

**Double-click:**
```
connect-to-ec2.bat
```

Or use PowerShell/CMD:
```powershell
ssh -i "C:\Users\HP\Desktop\Donnie\aws-factory-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
```

---

## 🔧 First-Time Setup on EC2

Once connected via SSH, run these commands:

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login for group changes
exit
```

### 3. Reconnect and Verify
```bash
# Reconnect
ssh -i "C:\Users\HP\Desktop\Donnie\aws-factory-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com

# Verify installations
docker --version
docker-compose --version
```

### 4. Deploy Application
```bash
cd ~/content-factory
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

---

## 📋 Post-Deployment

### Access Your Application

**Main Application:**
```
http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000
```

**API Documentation:**
```
http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/docs
```

**Health Check:**
```
http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health
```

**YouTube OAuth:**
```
http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth
```

---

## 🔐 IMPORTANT: Update Google OAuth

After deployment, you MUST update your Google OAuth settings:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: **APIs & Services → Credentials**
3. Select your OAuth Client ID: `143119762023-gphmghekf50hmb8lbh3s1uj6lctl6gha`
4. Add these redirect URIs:
   ```
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/oauth2callback
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com/api/v1/social-media/youtube/oauth2callback
   ```
5. Add these JavaScript origins:
   ```
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000
   http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
   ```
6. Click **Save**

---

## 🛠️ Useful Commands (On EC2)

### Check Application Status
```bash
cd ~/content-factory
docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f app
```

### Restart Application
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Stop Application
```bash
docker-compose -f docker-compose.prod.yml down
```

### Rebuild and Start
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Check Health
```bash
curl http://localhost:8000/health
```

---

## 🚨 Troubleshooting

### Can't connect via SSH?

**Check:**
1. EC2 instance is running in AWS Console
2. Security group allows SSH (port 22) from your IP
3. SSH key file permissions:
   ```powershell
   # In PowerShell, right-click the .pem file
   # Properties → Security → Advanced
   # Disable inheritance and remove all users except yourself
   ```

### Application not accessible?

**Check:**
1. Security group allows port 8000
2. Application is running:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```
3. Check logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs app
   ```

### Docker not working?

```bash
# Check if user is in docker group
groups ubuntu

# If not, add and logout/login
sudo usermod -aG docker ubuntu
exit
# Then reconnect
```

---

## 📊 Monitoring

### Check System Resources
```bash
# CPU and Memory
htop

# Disk space
df -h

# Docker stats
docker stats
```

### Check Application Logs
```bash
# Real-time logs
docker-compose -f docker-compose.prod.yml logs -f

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

---

## 🔄 Update Application

### From Your Windows Machine:

1. Make changes locally
2. Run:
   ```
   deploy-to-ec2.bat
   ```

### On EC2 (if using Git):

```bash
cd ~/content-factory
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🎯 Next Steps

1. ✅ Deploy application using `deploy-to-ec2.bat`
2. ✅ Update Google OAuth redirect URIs
3. ✅ Test YouTube authentication
4. ✅ Set up SSL/HTTPS (optional - see `SSL_HTTPS_SETUP.md`)
5. ✅ Configure monitoring (optional - see `CLOUDWATCH_MONITORING_SETUP.md`)
6. ✅ Set up auto-scaling (optional - see `AUTO_SCALING_SETUP.md`)

---

## 📞 Quick Reference

| Action | Command/File |
|--------|--------------|
| Deploy | `deploy-to-ec2.bat` |
| Connect via SSH | `connect-to-ec2.bat` |
| Application URL | http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000 |
| API Docs | http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/docs |
| Health Check | http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health |

---

## ✨ You're Ready!

Your EC2 instance is configured and ready for deployment. Simply run:

```
deploy-to-ec2.bat
```

And your Content Factory will be live in minutes! 🚀
