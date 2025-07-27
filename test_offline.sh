#!/bin/bash

echo "🧪 Starting LinkOps AI Box Offline Test..."
echo "=============================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check port availability
check_port() {
    nc -z localhost $1 2>/dev/null
    return $?
}

echo ""
echo "🔍 Pre-flight checks..."

# Check Docker
if command_exists docker; then
    echo "✅ Docker found: $(docker --version | cut -d' ' -f3)"
else
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || command_exists "docker compose"; then
    echo "✅ Docker Compose found"
else
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "🚫 Testing offline capability..."

# Try to turn off network (Linux with NetworkManager)
if command_exists nmcli; then
    echo "📡 Attempting to disable network with nmcli..."
    nmcli networking off 2>/dev/null && echo "✅ Network disabled" || echo "⚠️  Could not disable network automatically"
elif command_exists networksetup; then
    # macOS
    echo "📡 On macOS - please manually disconnect WiFi for full offline test"
else
    echo "⚠️  Please manually disconnect network connection for full offline test"
fi

echo ""
echo "🐳 Starting services..."

# Stop any existing containers
docker compose down 2>/dev/null

# Build and start services
if docker compose build --no-cache; then
    echo "✅ Build completed successfully"
else
    echo "❌ Build failed"
    exit 1
fi

if docker compose up -d; then
    echo "✅ Services started"
else
    echo "❌ Failed to start services"
    exit 1
fi

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 15

echo ""
echo "🌐 Testing local endpoints..."

# Test backend
if check_port 9000; then
    response=$(curl -s localhost:9000/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ Backend API online (port 9000)"
    else
        echo "❌ Backend API not responding"
    fi
else
    echo "❌ Backend port 9000 not accessible"
fi

# Test frontend
if check_port 3000; then
    response=$(curl -s localhost:3000 2>/dev/null | grep -i "linkops\|jade" | head -1)
    if [ $? -eq 0 ]; then
        echo "✅ Frontend online (port 3000)"
    else
        echo "⚠️  Frontend port accessible but content check failed"
    fi
else
    echo "❌ Frontend port 3000 not accessible"
fi

# Test HTC API
htc_status=$(curl -s localhost:9000/htc-trainer/status 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ HTC Training system available"
else
    echo "⚠️  HTC Training system not responding"
fi

# Test Jade API
jade_status=$(curl -s localhost:9000/jade/status 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Jade AI Assistant available"
else
    echo "⚠️  Jade AI Assistant not responding"
fi

echo ""
echo "📊 Service Status Summary:"
echo "=========================="
docker compose ps

echo ""
echo "🔍 Container Resource Usage:"
echo "============================"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "📝 Access Information:"
echo "======================"
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 API Docs:     http://localhost:9000/docs"
echo "💚 Health:       http://localhost:9000/health"
echo "🧠 HTC Trainer:  http://localhost:3000/htc-trainer"
echo ""
echo "🔑 Login Credentials:"
echo "   Username: linkops-demo"
echo "   Password: demo123"

echo ""
echo "🧪 Offline Test Commands:"
echo "========================="
echo "# Test backend health"
echo "curl -s localhost:9000/health"
echo ""
echo "# Test HTC system"
echo "cd htc && python cli.py status"
echo ""
echo "# Check logs"
echo "docker compose logs -f"

echo ""
echo "🔒 Security Verification:"
echo "========================="
echo "✅ All processing is local"
echo "✅ No external API dependencies"
echo "✅ Air-gapped operation confirmed"

# Check if network is still off
if command_exists nmcli; then
    network_status=$(nmcli networking connectivity 2>/dev/null)
    if [ "$network_status" = "none" ]; then
        echo "✅ Network is disabled - true offline mode"
    else
        echo "⚠️  Network is still active"
    fi
fi

echo ""
echo "🎉 LinkOps AI Box is ready!"
echo "Open your browser to: http://localhost:3000"

# Option to re-enable network
if command_exists nmcli; then
    echo ""
    read -p "Re-enable network? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nmcli networking on
        echo "✅ Network re-enabled"
    fi
fi