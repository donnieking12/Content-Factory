# 🚀 Production Deployment Guide

## API Keys Required for Production

### 1. OpenAI API Key (Required for AI Script Generation)
**Get Your Key:**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create new secret key
5. Copy the key (starts with `sk-...`)

**Add to `.env`:**
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

**Monthly Cost:** ~$10-50 depending on usage

### 2. Social Media API Keys

#### TikTok Business API
**Setup:**
1. Apply at [TikTok for Developers](https://developers.tiktok.com/)
2. Get approved for Business API
3. Create app and get credentials

**Add to `.env`:**
```env
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
```

#### Instagram Graph API
**Setup:**
1. Create [Meta for Developers](https://developers.facebook.com/) account
2. Create app and add Instagram Graph API
3. Get page access token

**Add to `.env`:**
```env
INSTAGRAM_CLIENT_ID=your_instagram_app_id
INSTAGRAM_CLIENT_SECRET=your_instagram_app_secret
INSTAGRAM_PAGE_ID=your_instagram_business_page_id
```

#### YouTube Data API
**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable YouTube Data API v3
3. Create API key or OAuth credentials

**Add to `.env`:**
```env
YOUTUBE_API_KEY=your_youtube_api_key
```

### 3. AI Avatar Service (HeyGen)
**Setup:**
1. Sign up at [HeyGen](https://www.heygen.com/)
2. Get API access
3. Copy API key from dashboard

**Add to `.env`:**
```env
AI_AVATAR_API_URL=https://api.heygen.com
AI_AVATAR_API_KEY=your_heygen_api_key
```

## Cloud Deployment Options

### Option A: AWS Deployment
- **Service:** AWS EC2 + RDS + ElastiCache
- **Cost:** ~$50-200/month
- **Pros:** Full control, scalable
- **Setup Time:** 2-4 hours

### Option B: Google Cloud Platform
- **Service:** GCP Compute Engine + Cloud SQL + Cloud Memorystore
- **Cost:** ~$40-150/month
- **Pros:** Good AI integration
- **Setup Time:** 2-3 hours

### Option C: Digital Ocean (Recommended for MVP)
- **Service:** Droplets + Managed Database + Redis
- **Cost:** ~$25-100/month
- **Pros:** Simple, cost-effective
- **Setup Time:** 1-2 hours

### Option D: Railway/Render (Easiest)
- **Service:** Platform-as-a-Service
- **Cost:** ~$20-80/month
- **Pros:** Zero DevOps, auto-deploy
- **Setup Time:** 30 minutes

## Quick Production Setup Commands

```bash
# 1. Update dependencies for production
pip install gunicorn redis celery[redis] sentry-sdk

# 2. Set production environment
export ENVIRONMENT=production

# 3. Start production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 4. Start Celery workers
celery -A celery_worker.celery_app worker --loglevel=info --concurrency=4

# 5. Start Celery beat scheduler
celery -A celery_worker.celery_app beat --loglevel=info
```

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong SECRET_KEY
- [ ] Enable CORS properly
- [ ] Use environment variables for all secrets
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Set up backup strategy

## Monitoring Setup

```bash
# Add to requirements.txt
sentry-sdk[fastapi]>=1.32.0
prometheus-client>=0.17.0
```

## Next Steps After API Keys
1. Test all integrations in development
2. Choose cloud provider
3. Set up CI/CD pipeline
4. Deploy to staging environment
5. Performance testing
6. Deploy to production