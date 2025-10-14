#!/bin/bash
# AI Content Factory - Production Deployment Script
# This script deploys your localhost app to Digital Ocean

echo "🚀 AI Content Factory - Production Deployment"
echo "=============================================="

# Step 1: Prepare production environment
echo "📦 Step 1: Preparing production environment..."
cp .env .env.prod
echo "ENVIRONMENT=production" >> .env.prod

# Step 2: Build production image
echo "🏗️  Step 2: Building production Docker image..."
docker build -f Dockerfile.prod -t content-factory:latest .

# Step 3: Test production build locally
echo "🧪 Step 3: Testing production build..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 15

# Health check
echo "🔍 Running health check..."
curl -f http://localhost/health || echo "⚠️  Health check failed - check logs"

echo "✅ Production build ready!"
echo ""
echo "📋 Next Steps:"
echo "1. Create Digital Ocean Droplet (Ubuntu 22.04, 2GB+ RAM)"
echo "2. Copy project files to server"
echo "3. Run: docker-compose -f docker-compose.prod.yml up -d"
echo "4. Configure domain and SSL"
echo ""
echo "🌐 Your app will be live at: https://your-domain.com"