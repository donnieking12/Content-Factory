# 🚀 Content Factory AI - Quick Start Guide

## Overview
This is an AI-powered content factory that discovers trending products, generates video scripts, creates videos with AI avatars, and publishes to social media platforms.

## 📋 Prerequisites

1. **Python 3.10+** - Download from [python.org](https://python.org) or Microsoft Store
2. **Git** (optional) - For version control
3. **API Keys** (for full functionality):
   - Supabase account (free)
   - OpenAI API key (for script generation)
   - Social media API keys (optional)

## ⚡ Quick Setup (5 minutes)

### Method 1: Automated Setup (Recommended)

1. **Install Python 3.10+** from [python.org](https://python.org) (make sure to check "Add to PATH")

2. **Run the setup script**:
   ```bash
   python setup_project.py
   ```

3. **Configure API keys** in the `.env` file (minimum required):
   - Get a free Supabase account at [supabase.com](https://supabase.com)
   - Create a new project and copy the URL and anon key
   - Update `.env` file with your credentials

4. **Start the application**:
   ```bash
   # Windows
   venv\Scripts\activate
   python run.py
   
   # macOS/Linux  
   source venv/bin/activate
   python run.py
   ```

### Method 2: Manual Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**:
   ```bash
   python setup_db.py
   ```

4. **Start application**:
   ```bash
   python run.py
   ```

## 🌐 Access the Application

Once running, you can access:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Minimum Configuration (to get started)
1. **Supabase** (free database):
   - Create account at [supabase.com](https://supabase.com)
   - Create new project
   - Copy URL and anon key to `.env` file

### Full Configuration (for all features)
2. **OpenAI API** (for AI script generation):
   - Get API key at [platform.openai.com](https://platform.openai.com)
   - Add to `.env` file

3. **Social Media APIs** (for publishing):
   - TikTok Business API
   - Instagram Graph API  
   - YouTube Data API

4. **AI Avatar Service** (for video generation):
   - HeyGen API key

## 🧪 Testing the Application

### Basic API Test
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test products endpoint
curl http://localhost:8000/api/v1/products/
```

### Discover Trending Products
```bash
curl -X POST http://localhost:8000/api/v1/products/discover-trending
```

### Generate Video for Product
```bash
curl -X POST http://localhost:8000/api/v1/videos/generate-for-product/1
```

## 🔄 Background Tasks (Optional)

For full functionality, start Celery workers:

1. **Install Redis** (for task queue):
   ```bash
   # Windows (using Docker)
   docker run -d -p 6379:6379 redis
   
   # macOS
   brew install redis
   
   # Linux
   sudo apt install redis
   ```

2. **Start Celery worker** (in new terminal):
   ```bash
   # Windows
   venv\Scripts\activate
   celery -A celery_worker.celery_app worker --loglevel=info
   
   # macOS/Linux
   source venv/bin/activate
   celery -A celery_worker.celery_app worker --loglevel=info
   ```

## 🎯 What Works Without API Keys

Even without all API keys configured, you can:

- ✅ Browse the API documentation
- ✅ Test basic CRUD operations for products/videos
- ✅ Use the product discovery service (uses free FakeStoreAPI)
- ✅ Generate template-based video scripts
- ✅ Test the workflow endpoints
- ✅ View health and monitoring dashboards

## 🚨 Troubleshooting

### Common Issues

1. **Python not found**:
   - Install Python 3.10+ from python.org
   - Make sure "Add to PATH" was checked during installation

2. **Import errors**:
   - Activate virtual environment first
   - Run `pip install -r requirements.txt`

3. **Database connection errors**:
   - Check Supabase credentials in `.env` file
   - Run `python setup_db.py` to create tables

4. **Port already in use**:
   - Change port in `run.py` or kill existing process

### Windows-Specific Issues

1. **Execution Policy Error**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **PowerShell Command Issues**:
   - Use Command Prompt instead of PowerShell
   - Or use Git Bash if available

## 📚 Next Steps

1. **Configure all API keys** for full functionality
2. **Deploy to production** using Docker
3. **Set up monitoring** and alerts
4. **Customize services** for your specific needs
5. **Add more e-commerce APIs** for product discovery

## 🆘 Need Help?

- Check the detailed documentation in the other `.md` files
- Review the logs in the terminal for specific error messages
- Ensure all prerequisites are installed correctly

---

**🎉 You're all set! Start building AI-powered content with the Content Factory!**