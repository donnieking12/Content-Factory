#!/bin/bash
# Content Factory - AWS EC2 Deployment Script
# Run this script on your EC2 instance

echo "🚀 Content Factory - EC2 Deployment"
echo "===================================="
echo "Instance: ec2-13-36-168-66.eu-west-3.compute.amazonaws.com"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if running on EC2
echo -e "${YELLOW}📋 Step 1: Checking environment...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    echo "Run: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    echo "Run: sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "Then: sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"

# Step 2: Check .env file
echo ""
echo -e "${YELLOW}📋 Step 2: Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your production credentials${NC}"
        echo "Run: nano .env"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found either. Please create .env file manually.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ .env file found${NC}"

# Step 3: Check Google OAuth credentials
if [ ! -f google_client_secret.json ]; then
    echo -e "${YELLOW}⚠️  google_client_secret.json not found${NC}"
    echo "YouTube OAuth will not work without this file."
fi

# Step 4: Set production environment variables
echo ""
echo -e "${YELLOW}📋 Step 3: Setting production environment...${NC}"

# Update .env with EC2 base URL if not already set
if ! grep -q "APP_BASE_URL" .env; then
    echo "APP_BASE_URL=http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000" >> .env
    echo -e "${GREEN}✅ Added APP_BASE_URL to .env${NC}"
fi

# Step 5: Stop existing containers
echo ""
echo -e "${YELLOW}📋 Step 4: Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Step 6: Pull latest images and build
echo ""
echo -e "${YELLOW}📋 Step 5: Building production images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Step 7: Start services
echo ""
echo -e "${YELLOW}📋 Step 6: Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Step 8: Wait for services to start
echo ""
echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"
sleep 10

# Step 9: Health check
echo ""
echo -e "${YELLOW}📋 Step 7: Running health check...${NC}"
max_attempts=5
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            echo -e "${RED}❌ Health check failed after $max_attempts attempts${NC}"
            echo "Check logs with: docker-compose -f docker-compose.prod.yml logs app"
            exit 1
        fi
        echo "Attempt $attempt/$max_attempts failed, retrying..."
        sleep 5
        ((attempt++))
    fi
done

# Step 10: Show status
echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo ""
echo "======================================"
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "======================================"
echo "🌐 Access your application at:"
echo "  - Main App: http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000"
echo "  - Health Check: http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/health"
echo "  - API Docs: http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/docs"
echo ""
echo "======================================"
echo "📋 Useful Commands:"
echo "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - Restart: docker-compose -f docker-compose.prod.yml restart"
echo "  - Stop: docker-compose -f docker-compose.prod.yml down"
echo "  - Status: docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "======================================"
echo "🔐 Next Steps:"
echo "  1. Test YouTube OAuth: http://ec2-13-36-168-66.eu-west-3.compute.amazonaws.com:8000/api/v1/social-media/youtube/auth"
echo "  2. Update Google OAuth redirect URIs in Google Cloud Console"
echo "  3. Configure SSL certificate for HTTPS"
echo "  4. Set up monitoring and alerts"
echo ""
echo -e "${GREEN}✅ Content Factory is live!${NC}"
