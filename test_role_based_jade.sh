#!/bin/bash

echo "🎭 Testing Jade's Role-Based Landing Experience"
echo "=============================================="

echo ""
echo "🔍 Testing role-specific responses..."

# Function to test role-based responses
test_role_response() {
    local question="$1"
    local role="$2" 
    local expected_keyword="$3"
    local description="$4"
    
    echo ""
    echo "📝 Testing: $description ($role)"
    echo "Question: $question"
    
    response=$(curl -s -X POST localhost:9000/jade/query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$question\", \"user_role\": \"$role\"}" | jq -r '.response' 2>/dev/null)
    
    if [[ $response == *"$expected_keyword"* ]]; then
        echo "✅ Response contains '$expected_keyword'"
    else
        echo "❌ Response missing '$expected_keyword'"
        echo "Got: ${response:0:150}..."
    fi
}

# Check if services are running
if ! curl -s localhost:9000/health > /dev/null; then
    echo "❌ Backend not running. Please start services first:"
    echo "   docker compose up -d"
    exit 1
fi

echo "✅ Backend is running"

echo ""
echo "🧪 Testing Role-Specific Responses"
echo "==================================="

# Test Cloud Engineer responses
echo ""
echo "☁️ CLOUD ENGINEER RESPONSES:"
test_role_response "Show me the Docker architecture" "cloud_engineer" "Docker" "Infrastructure question"
test_role_response "Explain the security model" "cloud_engineer" "security" "Security architecture"
test_role_response "What about deployment automation?" "cloud_engineer" "deployment" "DevOps automation"

# Test AI/ML Engineer responses  
echo ""
echo "🧬 AI/ML ENGINEER RESPONSES:"
test_role_response "Show me LLM integration details" "ai_ml_engineer" "LLM" "AI integration"
test_role_response "How does ML pipeline work?" "ai_ml_engineer" "pipeline" "ML workflow"
test_role_response "Tell me about model training" "ai_ml_engineer" "training" "Model development"

# Test Property Manager responses
echo ""
echo "🏢 PROPERTY MANAGER RESPONSES:"
test_role_response "How can this help with vendors?" "property_manager" "vendor" "Vendor management"
test_role_response "What about tenant data?" "property_manager" "tenant" "Tenant management"
test_role_response "Show me maintenance automation" "property_manager" "maintenance" "Operations automation"

echo ""
echo "🎯 Role-Based Landing Experience Features:"
echo "=========================================="
echo ""
echo "✅ **Initial Flow:**"
echo "   1. Jade greets visitor"
echo "   2. Asks for role selection"
echo "   3. Provides tailored walkthrough"
echo ""
echo "✅ **Role Options:**"
echo "   ☁️  Cloud Engineer - DevOps/Infrastructure focus"
echo "   🧬 AI/ML Engineer - Machine Learning focus" 
echo "   🏢 Property Manager - Business operations focus"
echo ""
echo "✅ **Personalized Experience:**"
echo "   • Role-specific introduction scripts"
echo "   • Tailored quick action buttons"
echo "   • Context-aware responses"
echo "   • Appropriate technical depth"

echo ""
echo "🎬 Demo Scenario Walkthroughs:"
echo "============================="
echo ""
echo "☁️ **Cloud Engineer Path:**"
echo "   • Jade explains Docker architecture"
echo "   • Shows security hardening"
echo "   • Demonstrates deployment automation"
echo "   • Highlights DevSecOps practices"
echo ""
echo "🧬 **AI/ML Engineer Path:**"
echo "   • Jade shows LLM integration"
echo "   • Explains ML pipeline automation"
echo "   • Demonstrates HTC autonomous learning"
echo "   • Highlights technical capabilities"
echo ""
echo "🏢 **Property Manager Path:**"
echo "   • Jade explains privacy benefits"
echo "   • Shows vendor management tools"
echo "   • Demonstrates cost prediction"
echo "   • Highlights business value"

echo ""
echo "💬 Role-Specific Questions to Try:"
echo "=================================="
echo ""
echo "☁️ **For Cloud Engineers:**"
echo "   • 'Show me the Docker architecture'"
echo "   • 'Explain the security model'"
echo "   • 'How do you handle deployment?'"
echo "   • 'What about infrastructure monitoring?'"
echo ""
echo "🧬 **For AI/ML Engineers:**"
echo "   • 'LLM integration details'"
echo "   • 'ML pipeline automation'"
echo "   • 'How does the HTC system work?'"
echo "   • 'Show me model training workflows'"
echo ""
echo "🏢 **For Property Managers:**"
echo "   • 'Vendor management demo'"
echo "   • 'How do you protect tenant data?'"
echo "   • 'Show me maintenance automation'"
echo "   • 'Cost prediction models'"

echo ""
echo "🌐 Experience the Role-Based Landing:"
echo "===================================="
echo "1. Open: http://localhost:3000"
echo "2. Watch Jade's introduction"
echo "3. Select your role when prompted"
echo "4. Experience personalized walkthrough"
echo "5. Ask role-specific questions"

echo ""
echo "🎉 Role-based Jade experience is ready!"
echo "Each visitor gets a personalized AI introduction!"

# Optional: Open browser
if command -v xdg-open > /dev/null; then
    read -p "Open the role-based landing experience? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:3000
    fi
elif command -v open > /dev/null; then
    read -p "Open the role-based landing experience? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
fi