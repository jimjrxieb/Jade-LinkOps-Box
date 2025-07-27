#!/bin/bash

echo "🎯 Jade's Complete Walkthrough Test"
echo "==================================="

echo ""
echo "🔍 Testing Jade's specialized responses..."

# Function to test Jade response
test_jade_response() {
    local question="$1"
    local expected_keyword="$2"
    local description="$3"
    
    echo ""
    echo "📝 Testing: $description"
    echo "Question: $question"
    
    response=$(curl -s -X POST localhost:9000/jade/query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$question\"}" | jq -r '.response' 2>/dev/null)
    
    if [[ $response == *"$expected_keyword"* ]]; then
        echo "✅ Response contains '$expected_keyword'"
    else
        echo "❌ Response missing '$expected_keyword'"
        echo "Got: ${response:0:100}..."
    fi
}

# Check if services are running
if ! curl -s localhost:9000/health > /dev/null; then
    echo "❌ Backend not running. Please start services first:"
    echo "   docker compose up -d"
    exit 1
fi

echo "✅ Backend is running"

# Test specialized responses
test_jade_response "Give me a walkthrough" "guided tour" "Walkthrough request"
test_jade_response "Property management use cases" "property management" "Property management inquiry"
test_jade_response "For AI/ML interviewers" "AI/ML engineering" "Technical interviewer mode"
test_jade_response "What is the HTC system?" "Hyperbolic Time Chamber" "HTC explanation"
test_jade_response "Building tools demo" "tool creation" "Tool building demo"
test_jade_response "Privacy and security features" "enterprise privacy" "Security features"

echo ""
echo "🧪 Testing HTC training with sample data..."

# Test HTC CLI with sample data
cd htc
echo ""
echo "📊 Sample vendor performance data:"
head -3 intake/uploaded_docs/vendor_performance.csv

echo ""
echo "🏠 Sample maintenance requests:"
head -3 intake/uploaded_docs/maintenance_requests.csv

echo ""
echo "🔧 Testing HTC CLI status:"
python cli.py status

echo ""
echo "🌐 Complete Jade Experience URLs:"
echo "================================="
echo ""
echo "🏠 Landing Page:      http://localhost:3000/"
echo "   • Jade's auto-introduction"
echo "   • Interactive chat with specialized responses"
echo "   • Quick action buttons for common questions"
echo ""
echo "📊 Dashboard:         http://localhost:3000/dashboard"  
echo "   • Platform overview and stats"
echo "   • Navigation to all features"
echo ""
echo "🧠 HTC Training:      http://localhost:3000/htc-trainer"
echo "   • Upload files for autonomous learning"
echo "   • Generate tools, models, knowledge, actions"
echo ""
echo "📚 API Docs:          http://localhost:9000/docs"
echo "   • Complete API documentation"
echo "   • Interactive endpoint testing"

echo ""
echo "💬 Key Questions to Ask Jade:"
echo "============================"
echo ""
echo "🎯 **For Walkthroughs:**"
echo "   • 'Give me a walkthrough'"
echo "   • 'Show me what you can do'"
echo ""
echo "🏢 **For Enterprise/Property Management:**"
echo "   • 'Property management use cases'"
echo "   • 'How can you help with vendor management?'"
echo "   • 'Create a tool for maintenance requests'"
echo ""
echo "👨‍💼 **For AI/ML Interviewers:**"
echo "   • 'For AI/ML interviewers'"
echo "   • 'What technical skills does this demonstrate?'"
echo "   • 'Show me the ML engineering capabilities'"
echo ""
echo "🧠 **For HTC Learning:**"
echo "   • 'What is the HTC system?'"
echo "   • 'How does autonomous learning work?'"
echo "   • 'Can you learn from my data?'"
echo ""
echo "🔧 **For Tool Building:**"
echo "   • 'Building tools demo'"
echo "   • 'Create a vendor ranking tool'"
echo "   • 'How do you generate automation scripts?'"
echo ""
echo "🔒 **For Security/Privacy:**"
echo "   • 'Privacy and security features'"
echo "   • 'Why is this air-gapped?'"
echo "   • 'How do you protect sensitive data?'"

echo ""
echo "🎭 Demo Scenarios:"
echo "=================="
echo ""
echo "🏢 **Property Management Demo:**"
echo "   1. Ask: 'Property management use cases'"
echo "   2. Navigate to HTC Trainer"
echo "   3. Upload vendor_performance.csv"
echo "   4. Task: 'Create a vendor ranking system'"
echo "   5. Generate tool + model + knowledge"
echo ""
echo "👨‍💼 **Technical Interview Demo:**"
echo "   1. Ask: 'For AI/ML interviewers'"
echo "   2. Ask: 'Show me ML model training'"
echo "   3. Upload maintenance_requests.csv"
echo "   4. Train urgency prediction model"
echo "   5. Demonstrate full ML pipeline"
echo ""
echo "🧠 **HTC Learning Demo:**"
echo "   1. Ask: 'What is the HTC system?'"
echo "   2. Ask: 'Give me a walkthrough'"
echo "   3. Upload any CSV or text file"
echo "   4. Describe what you want to learn"
echo "   5. Watch autonomous generation"

echo ""
echo "🎉 Jade's walkthrough system is ready!"
echo "Open http://localhost:3000 to experience the complete AI-driven introduction!"

# Optional: Open browser
if command -v xdg-open > /dev/null; then
    read -p "Open Jade's landing page? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:3000
    fi
elif command -v open > /dev/null; then
    read -p "Open Jade's landing page? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
fi