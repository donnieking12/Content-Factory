# SSL/HTTPS Setup with Let's Encrypt - Content Factory

## 🔒 Configure HTTPS for Production

This guide shows you how to secure your Content Factory application with free SSL certificates from Let's Encrypt.

---

## 📋 Prerequisites

- ✅ EC2 instance running and accessible
- ✅ Custom domain name (e.g., `contentfactory.yourdomain.com`)
- ✅ Domain DNS pointing to EC2 IP: `13.36.168.66`
- ✅ Port 80 and 443 open in AWS Security Group

---

## 🌐 Step 1: Configure Domain DNS

### In Your Domain Registrar (GoDaddy, Namecheap, etc.):

Add an **A Record**:
```
Type: A
Name: contentfactory (or @ for root domain)
Value: 13.36.168.66
TTL: 600 (or default)
```

Wait 5-10 minutes for DNS propagation, then verify:
```bash
nslookup contentfactory.yourdomain.com
# Should return: 13.36.168.66
```

---

## 🔧 Step 2: Install Nginx and Certbot

**SSH to your EC2 instance:**

```bash
ssh -i "your-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
```

**Install Nginx:**

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Install Certbot:**

```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

## 📝 Step 3: Configure Nginx for Content Factory

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/contentfactory
```

**Add this configuration:**

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name contentfactory.yourdomain.com;
    
    # Allow Certbot to validate domain
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server (will be configured by Certbot)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name contentfactory.yourdomain.com;
    
    # SSL certificates (Certbot will add these)
    # ssl_certificate /etc/letsencrypt/live/contentfactory.yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/contentfactory.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy settings
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Increase timeouts for long-running requests
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    
    # Proxy to Content Factory app
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000/api/;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
    
    # Static files (if needed)
    location /static/ {
        alias /home/ubuntu/content-factory/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable the site:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/contentfactory /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 🔐 Step 4: Obtain SSL Certificate

**Run Certbot:**

```bash
sudo certbot --nginx -d contentfactory.yourdomain.com
```

**Follow the prompts:**
1. Enter your email address
2. Agree to Terms of Service
3. Choose whether to share email (optional)
4. Certbot will automatically configure SSL in Nginx

**Expected output:**
```
Congratulations! You have successfully enabled HTTPS on https://contentfactory.yourdomain.com
```

---

## 🔄 Step 5: Set Up Auto-Renewal

Certbot automatically sets up a cron job for renewal. Verify it:

```bash
# Test renewal process (dry run)
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

**Manual renewal (if needed):**
```bash
sudo certbot renew
sudo systemctl reload nginx
```

---

## 🔧 Step 6: Update Application Configuration

**Update `.env` file on EC2:**

```bash
cd ~/content-factory
nano .env
```

**Change APP_BASE_URL to HTTPS:**

```env
# OLD:
# APP_BASE_URL=http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000

# NEW:
APP_BASE_URL=https://contentfactory.yourdomain.com
```

**Restart application:**

```bash
docker-compose -f docker-compose.prod.yml restart app
```

---

## 🔐 Step 7: Update Google OAuth Redirect URIs

**In Google Cloud Console:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: `ai-content-prod`
3. Navigate to: APIs & Services → Credentials
4. Update OAuth 2.0 Client ID

**Add HTTPS redirect URIs:**

```
https://contentfactory.yourdomain.com/api/v1/social-media/youtube/oauth2callback
```

**Add HTTPS JavaScript origins:**

```
https://contentfactory.yourdomain.com
```

**Update `google_client_secret.json` on EC2:**

```bash
cd ~/content-factory
nano google_client_secret.json
```

Add HTTPS URLs to the arrays:

```json
{
  "web": {
    "redirect_uris": [
      "http://localhost:8000/api/v1/social-media/youtube/oauth2callback",
      "https://contentfactory.yourdomain.com/api/v1/social-media/youtube/oauth2callback"
    ],
    "javascript_origins": [
      "http://localhost:8000",
      "https://contentfactory.yourdomain.com"
    ]
  }
}
```

---

## 🧪 Step 8: Test HTTPS Setup

### Test SSL Certificate:

```bash
# Check SSL certificate
curl -I https://contentfactory.yourdomain.com/health

# Test with SSL Labs
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=contentfactory.yourdomain.com
```

### Test Application:

```bash
# Health check
curl https://contentfactory.yourdomain.com/health

# API endpoints
curl https://contentfactory.yourdomain.com/api/v1/products/

# YouTube OAuth
curl https://contentfactory.yourdomain.com/api/v1/social-media/youtube/auth-status
```

### Test HTTP to HTTPS Redirect:

```bash
# Should redirect to HTTPS
curl -I http://contentfactory.yourdomain.com
```

---

## 📊 Step 9: Configure Security Headers

Nginx is already configured with security headers, but verify:

```bash
curl -I https://contentfactory.yourdomain.com
```

**Should include:**
- `Strict-Transport-Security: max-age=31536000`
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

---

## 🔧 Advanced Nginx Optimizations

### Enable Rate Limiting

Add to Nginx config before `server` block:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/s;

server {
    # ... existing config ...
    
    # Apply rate limiting to API
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://localhost:8000/api/;
    }
    
    # General rate limiting
    location / {
        limit_req zone=general_limit burst=50 nodelay;
        proxy_pass http://localhost:8000;
    }
}
```

### Enable Gzip Compression

Add to `http` block in `/etc/nginx/nginx.conf`:

```nginx
http {
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    
    # ... rest of config
}
```

### Enable HTTP/2

HTTP/2 is already enabled with `listen 443 ssl http2;` in the config.

---

## 🔄 Certificate Renewal

Certbot automatically renews certificates. Check renewal:

```bash
# View renewal configuration
sudo cat /etc/letsencrypt/renewal/contentfactory.yourdomain.com.conf

# Test renewal
sudo certbot renew --dry-run

# Force renewal (if needed, certificates must be <30 days from expiry)
sudo certbot renew --force-renewal
```

---

## 🚨 Troubleshooting

### Issue: Certificate request fails

**Check:**
```bash
# Verify DNS is pointing to correct IP
nslookup contentfactory.yourdomain.com

# Verify port 80 is accessible
curl -I http://contentfactory.yourdomain.com

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Issue: HTTPS not working after certificate installation

**Solution:**
```bash
# Check Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check SSL certificate
sudo certbot certificates
```

### Issue: Mixed content warnings

**Solution:** Ensure all resources use HTTPS URLs in your application.

---

## 📝 Maintenance Checklist

- [ ] Certificate auto-renewal is working
- [ ] HTTP redirects to HTTPS
- [ ] Security headers are present
- [ ] Rate limiting is configured
- [ ] Gzip compression enabled
- [ ] SSL Labs test shows A+ rating
- [ ] All API endpoints work over HTTPS
- [ ] YouTube OAuth works with HTTPS

---

## 🎯 Final URLs

After SSL setup, your application will be accessible at:

- **Main App:** https://contentfactory.yourdomain.com
- **API Docs:** https://contentfactory.yourdomain.com/docs
- **Health Check:** https://contentfactory.yourdomain.com/health
- **YouTube OAuth:** https://contentfactory.yourdomain.com/api/v1/social-media/youtube/auth

---

## ✅ Success!

Your Content Factory is now secured with HTTPS! 🔒

**Benefits:**
- ✅ Encrypted traffic
- ✅ Browser trust indicators
- ✅ SEO benefits
- ✅ Required for many OAuth providers
- ✅ Professional appearance

**Next Steps:**
- Set up CloudWatch monitoring
- Configure auto-scaling
- Implement CI/CD pipeline
