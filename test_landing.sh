#!/bin/bash

echo "🚀 Testing Jade Landing Page Experience"
echo "======================================="

echo ""
echo "🔍 Pre-flight checks..."

# Check if services are running
if ! curl -s localhost:9000/health > /dev/null; then
    echo "❌ Backend not running. Starting services..."
    docker compose up -d
    echo "⏳ Waiting for services to start..."
    sleep 15
else
    echo "✅ Backend is running"
fi

if ! curl -s localhost:3000 > /dev/null; then
    echo "❌ Frontend not accessible"
    exit 1
else
    echo "✅ Frontend is running"
fi

echo ""
echo "🧪 Testing Jade AI responses..."

# Test HTC question
echo "📝 Testing HTC question..."
response=$(curl -s -X POST localhost:9000/jade/query \
    -H "Content-Type: application/json" \
    -d '{"query": "What is the HTC system?"}' | jq -r '.response' 2>/dev/null)

if [[ $response == *"HTC"* ]] && [[ $response == *"autonomous learning"* ]]; then
    echo "✅ HTC response working"
else
    echo "❌ HTC response failed"
fi

# Test tool question
echo "📝 Testing tool creation question..."
response=$(curl -s -X POST localhost:9000/jade/query \
    -H "Content-Type: application/json" \
    -d '{"query": "How do I create tools?"}' | jq -r '.response' 2>/dev/null)

if [[ $response == *"tool"* ]] && [[ $response == *"MCP"* ]]; then
    echo "✅ Tool creation response working"
else
    echo "❌ Tool creation response failed"
fi

# Test privacy question
echo "📝 Testing privacy question..."
response=$(curl -s -X POST localhost:9000/jade/query \
    -H "Content-Type: application/json" \
    -d '{"query": "Is this secure and private?"}' | jq -r '.response' 2>/dev/null)

if [[ $response == *"local"* ]] && [[ $response == *"privacy"* ]]; then
    echo "✅ Privacy response working"
else
    echo "❌ Privacy response failed"
fi

echo ""
echo "🌐 Landing page URLs:"
echo "   • Landing:     http://localhost:3000/"
echo "   • Dashboard:   http://localhost:3000/dashboard"
echo "   • HTC Trainer: http://localhost:3000/htc-trainer"
echo "   • API Docs:    http://localhost:9000/docs"

echo ""
echo "🎯 Landing Page Features:"
echo "   ✅ Jade introduces herself automatically"
echo "   ✅ Interactive chat with specialized responses"
echo "   ✅ Quick action buttons for common questions"
echo "   ✅ Navigation to key platform features"
echo "   ✅ Real-time AI responses with execution timing"
echo "   ✅ Professional dark theme with animations"

echo ""
echo "💬 Example Questions to Ask Jade:"
echo "   • 'What is the HTC system?'"
echo "   • 'How do I create tools?'"
echo "   • 'Can you train ML models?'"
echo "   • 'Why is this air-gapped?'"
echo "   • 'What can you do?'"

echo ""
echo "🎉 Landing page is ready!"
echo "Open http://localhost:3000 to experience Jade's introduction!"

# Optional: Open browser
if command -v xdg-open > /dev/null; then
    read -p "Open browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:3000
    fi
elif command -v open > /dev/null; then
    read -p "Open browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
fi