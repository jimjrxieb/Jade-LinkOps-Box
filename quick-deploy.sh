#!/bin/bash

echo "⚡ Quick Deploy - LinkOps AI Box"
echo "================================"

# Quick deployment for testing and demo purposes
# This gets you up and running in under 5 minutes

set -e  # Exit on error

echo ""
echo "🔍 Quick checks..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Download model if not present (quick version)
MODEL_FILE="rag/llm_weights/mistral.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    echo ""
    echo "📥 Downloading AI model (this may take a few minutes)..."
    echo "💡 Tip: This only happens once. Future deployments will be instant!"
    
    mkdir -p rag/llm_weights
    
    # Use the smaller Q2_K model for quick deployment
    wget --progress=bar:force:noscroll \
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q2_K.gguf" \
        -O "$MODEL_FILE"
    
    echo "✅ Model downloaded successfully"
else
    echo "✅ AI model ready"
fi

# Stop any existing containers
echo ""
echo "🛑 Stopping any existing containers..."
docker compose down 2>/dev/null || true

# Quick build and start
echo ""
echo "🚀 Building and starting services..."
docker compose build --parallel
docker compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to start..."

wait_for_service() {
    local url=$1
    local name=$2
    
    for i in {1..20}; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo "✅ $name is ready"
            return 0
        fi
        echo "⏳ Starting $name... ($i/20)"
        sleep 3
    done
    
    echo "❌ $name failed to start"
    return 1
}

wait_for_service "http://localhost:9000/health" "Backend"
wait_for_service "http://localhost:3000" "Frontend" 

# Quick test
echo ""
echo "🧪 Quick test..."
response=$(curl -s -X POST localhost:9000/jade/query \
    -H "Content-Type: application/json" \
    -d '{"query": "Hello Jade!", "user_role": "ai_ml_engineer"}' | jq -r '.response' 2>/dev/null)

if [[ $response == *"Hello"* ]] || [[ $response == *"Hi"* ]]; then
    echo "✅ Jade is responding!"
else
    echo "⚠️  Jade might need a moment to warm up"
fi

# Success!
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "🌐 Access Jade:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:9000/docs"
echo ""
echo "🎯 Try These URLs:"
echo "   Landing:     http://localhost:3000/"
echo "   Dashboard:   http://localhost:3000/dashboard"
echo "   HTC Trainer: http://localhost:3000/htc-trainer"
echo ""
echo "🔐 Demo Login: linkops-demo / demo123"
echo ""
echo "💡 Next Steps:"
echo "   1. Visit the landing page and select your role"
echo "   2. Chat with Jade about your interests"
echo "   3. Try the HTC trainer with your own data"
echo "   4. Share the demo with others!"

echo ""
echo "📊 Container Status:"
docker compose ps

echo ""
echo "🛠️  Management Commands:"
echo "   View logs:    docker compose logs -f"
echo "   Stop:         docker compose down"
echo "   Restart:      ./quick-deploy.sh"

# Optional browser opening
if command -v xdg-open >/dev/null 2>&1; then
    echo ""
    read -p "🌐 Open Jade in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open "http://localhost:3000" 2>/dev/null &
    fi
elif command -v open >/dev/null 2>&1; then
    echo ""
    read -p "🌐 Open Jade in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "http://localhost:3000" 2>/dev/null &
    fi
fi

echo ""
echo "✨ Jade is ready to demonstrate adaptive AI!"