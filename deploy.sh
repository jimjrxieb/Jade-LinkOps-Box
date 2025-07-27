#!/bin/bash

echo "🚀 LinkOps AI Box - Production Deployment Script"
echo "=============================================="

# Configuration
DOMAIN=${DOMAIN:-"localhost"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
ENABLE_SSL=${ENABLE_SSL:-"false"}
BACKUP_DATA=${BACKUP_DATA:-"true"}

echo ""
echo "📋 Deployment Configuration:"
echo "   Domain: $DOMAIN"
echo "   Environment: $ENVIRONMENT" 
echo "   SSL: $ENABLE_SSL"
echo "   Backup: $BACKUP_DATA"

# Pre-deployment checks
echo ""
echo "🔍 Pre-deployment checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Check ports
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

echo "🔌 Checking ports..."
check_port 3000 || echo "   Frontend port conflict detected"
check_port 9000 || echo "   Backend port conflict detected"

# Create production environment file
echo ""
echo "📝 Creating production environment..."

cat > .env.production << EOF
# LinkOps AI Box - Production Configuration
NODE_ENV=production
ENVIRONMENT=production

# Domain Configuration
DOMAIN=$DOMAIN
FRONTEND_URL=http://$DOMAIN:3000
BACKEND_URL=http://$DOMAIN:9000

# Security Settings
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Database Settings
POSTGRES_DB=linkops_prod
POSTGRES_USER=linkops
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# AI Model Settings
LLM_MODEL_PATH=rag/llm_weights/mistral.gguf
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=512

# Resource Limits
MAX_UPLOAD_SIZE=100MB
SESSION_TIMEOUT=3600

# Privacy Settings
AUTO_CLEANUP_ON_LOGOUT=true
CLEANUP_TEMP_FILES=true

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO

# Performance
REDIS_URL=redis://redis:6379
ENABLE_CACHING=true
EOF

echo "✅ Production environment configured"

# Download AI model if not present
echo ""
echo "🧠 Checking AI model..."

MODEL_FILE="rag/llm_weights/mistral.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo "📥 Downloading Mistral 7B model (this may take a while)..."
    mkdir -p rag/llm_weights
    
    # Download with progress bar
    wget --progress=bar:force:noscroll \
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf" \
        -O "$MODEL_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ Model downloaded successfully"
    else
        echo "❌ Model download failed. Check your internet connection."
        exit 1
    fi
else
    echo "✅ AI model already present"
fi

# Create backup if requested
if [ "$BACKUP_DATA" = "true" ]; then
    echo ""
    echo "💾 Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup important directories
    cp -r db/ "$BACKUP_DIR/" 2>/dev/null || true
    cp -r htc/test_history/ "$BACKUP_DIR/" 2>/dev/null || true
    cp .env.production "$BACKUP_DIR/"
    
    echo "✅ Backup created at $BACKUP_DIR"
fi

# Build production images
echo ""
echo "🏗️  Building production images..."

# Use production docker-compose file
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - VITE_API_URL=http://localhost:9000
    depends_on:
      - unified-api
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  unified-api:
    build:
      context: ./unified-api
      dockerfile: Dockerfile
    ports:
      - "9000:9000"
    volumes:
      - ./rag:/app/rag
      - ./htc:/app/htc
      - ./db:/app/db
    environment:
      - ENVIRONMENT=production
      - PYTHONPATH=/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: linkops-network
EOF

# Build and start services
echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Check the logs above."
    exit 1
fi

echo ""
echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."

wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $name is ready"
            return 0
        fi
        
        echo "⏳ Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo "❌ $name failed to start"
    return 1
}

wait_for_service "http://localhost:9000/health" "Backend API"
wait_for_service "http://localhost:3000" "Frontend"

# Run post-deployment tests
echo ""
echo "🧪 Running deployment tests..."

# Test Jade's role-based responses
test_jade_response() {
    local role=$1
    local question=$2
    
    response=$(curl -s -X POST localhost:9000/jade/query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$question\", \"user_role\": \"$role\"}" | jq -r '.response' 2>/dev/null)
    
    if [[ $response == *"error"* ]] || [[ -z "$response" ]] || [[ "$response" == "null" ]]; then
        echo "❌ $role response test failed"
        return 1
    else
        echo "✅ $role response test passed"
        return 0
    fi
}

test_jade_response "ai_ml_engineer" "What is the HTC system?"
test_jade_response "cloud_engineer" "Show me the security model"
test_jade_response "property_manager" "How do you protect tenant data?"

# Test HTC system
echo "🧠 Testing HTC system..."
cd htc
python cli.py status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ HTC system operational"
else
    echo "⚠️  HTC system needs attention"
fi
cd ..

# Show deployment status
echo ""
echo "📊 Deployment Status:"
echo "===================="
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "🎯 Jade Landing:     http://$DOMAIN:3000"
echo "📊 Dashboard:        http://$DOMAIN:3000/dashboard"
echo "🧠 HTC Trainer:      http://$DOMAIN:3000/htc-trainer"
echo "📚 API Docs:         http://$DOMAIN:9000/docs"
echo "💚 Health Check:     http://$DOMAIN:9000/health"

echo ""
echo "🔐 Security Information:"
echo "========================"
echo "• All data processing happens locally"
echo "• No external API connections required"
echo "• Session data auto-cleanup enabled"
echo "• Production environment configured"

echo ""
echo "📋 Management Commands:"
echo "======================="
echo "• View logs:      docker-compose -f docker-compose.prod.yml logs -f"
echo "• Stop services:  docker-compose -f docker-compose.prod.yml down"
echo "• Restart:        docker-compose -f docker-compose.prod.yml restart"
echo "• Update:         ./deploy.sh"

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo "Jade AI Box is now running in production mode."
echo "Visit http://$DOMAIN:3000 to experience the adaptive AI platform!"

# Optional: Open browser
if command -v xdg-open > /dev/null; then
    read -p "Open Jade in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open "http://$DOMAIN:3000"
    fi
elif command -v open > /dev/null; then
    read -p "Open Jade in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "http://$DOMAIN:3000"
    fi
fi