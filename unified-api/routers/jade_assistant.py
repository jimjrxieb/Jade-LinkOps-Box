import re
import os
import sys
from typing import Dict, List, Optional, Any

import httpx
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

# Add rag module to path for imports
rag_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'rag')
if rag_path not in sys.path:
    sys.path.append(rag_path)

# Set model path relative to unified-api directory
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'rag', 'llm_weights', 'mistral.gguf')

try:
    from logic.llm_runner import generate_answer, get_llm_runner
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import LLM runner: {e}")
    LLM_AVAILABLE = False

# from rag.search import semantic_search
# from rag.logic.search import semantic_search as rag_semantic_search
# from logic.executor import execute_tool_by_name

router = APIRouter()


class JadeQuery(BaseModel):
    query: str
    context: Optional[List[Dict]] = []
    user_role: Optional[str] = None  # cloud_engineer, ai_ml_engineer, property_manager


class Source(BaseModel):
    content: str
    file: str
    score: float
    highlight: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    tool_run: Optional[Dict] = None


def detect_tool_command(message: str) -> Optional[str]:
    """Extract tool name from command like 'run tool X'."""
    pattern = r"run\s+tool\s+(\w+)"
    match = re.search(pattern, message.lower())
    return match.group(1) if match else None

def get_specialized_response(query: str, user_role: Optional[str] = None) -> Optional[str]:
    """Get specialized responses for common landing page questions."""
    query_lower = query.lower()
    
    # Role-specific context prefix
    role_context = ""
    if user_role == "cloud_engineer":
        role_context = "DevOps/Infrastructure focus: "
    elif user_role == "ai_ml_engineer": 
        role_context = "AI/ML Engineering focus: "
    elif user_role == "property_manager":
        role_context = "Property Management focus: "
    
    # Walkthrough requests
    if any(keyword in query_lower for keyword in ['walkthrough', 'demo', 'show me', 'guide me', 'tour']):
        return """🎯 **Perfect! Let me give you a guided tour of what I can do.**

I'll walk you through each capability step by step. Here are your options:

🔧 **1. Building Tools** - See me create automation scripts from scratch
📊 **2. Training Models** - Watch me train ML models on real data  
🛡️ **3. Privacy & Security** - Learn how everything stays local and secure
🧠 **4. HTC Learning** - Experience my autonomous learning chamber
🏢 **5. Enterprise Use Cases** - Property management and business scenarios

Just click any option above or type the number you'd like to explore first!

*This demo showcases real AI/ML engineering skills - not just API integrations.*"""

    # Property management specific
    elif any(keyword in query_lower for keyword in ['property', 'management', 'tenant', 'lease', 'maintenance', 'hvac', 'vendor']):
        return """🏢 **Excellent question! I'm specifically designed for companies like property management firms.**

**Why property managers love the AI Box:**

🔐 **Data Privacy**: Tenant information never leaves your servers
📊 **Custom Models**: Train on your work orders, vendor performance, tenant data
🤖 **Automation**: Generate reports, answer policy questions, rank vendors
🛠️ **No-Code Tools**: Anyone can use it - no AI background required

**Real Example:**
Upload your HVAC vendor data → I create a tool that suggests the best vendor based on cost, response time, and quality ratings. All without exposing sensitive tenant information to cloud services.

**Perfect for:**
- Vendor performance analysis
- Maintenance cost prediction  
- Tenant screening automation
- Policy Q&A systems
- Custom report generation

Want to see a live demo with property management data?"""

    # HTC System questions
    elif any(keyword in query_lower for keyword in ['htc', 'hyperbolic', 'time chamber', 'autonomous learning', 'train jade']):
        return """🧠 **The HTC (Hyperbolic Time Chamber)** - my personal training ground!

**This is where I become truly powerful:**

Instead of just using pre-trained models, I **learn from YOUR specific data and requirements**.

**How it works:**
1. **Upload any files** - CSV data, docs, code, policies
2. **Describe your goal** - "rank vendors", "predict maintenance costs", "automate reports"  
3. **I automatically generate:**
   - 🔧 Custom Python tools
   - 🤖 Trained ML models
   - 📚 Knowledge base entries
   - ⚡ Executable workflows

**Enterprise Example:**
*"Jade, learn our vendor evaluation process and create an automated ranking system"*

→ I analyze your vendor data, build a scoring model, create a tool interface, and deploy it instantly.

**This proves real AI/ML skills:** model training, feature engineering, automation, and deployment - not just API calls.

Ready to enter the HTC and train me on something?"""

    # Tool creation questions
    elif any(keyword in query_lower for keyword in ['tool', 'create tool', 'mcp', 'automation', 'build', 'script']):
        return """🔧 **Let me show you real tool creation in action!**

**This isn't just code generation - it's full automation engineering:**

**What I can build:**
- 📊 Data analysis and reporting tools
- 🔄 File processing and automation scripts  
- 🌐 API integration and webhook handlers
- 📈 Custom dashboard and visualization tools
- 🔍 Data validation and quality checking tools

**The Process:**
1. **You describe the need** - "I need to process vendor invoices"
2. **I generate Python code** - Complete, executable, well-documented
3. **Tool becomes available** - Instantly usable through the platform
4. **You run it anytime** - No coding required

**Enterprise Example:**
*"Create a tool that reads maintenance requests from CSV and generates priority scores"*

→ I build a complete tool with input validation, scoring algorithms, and output formatting.

**This demonstrates:** Software engineering, API design, data processing, and deployment automation.

Want to build a tool right now? Describe what you need!"""

    # Interviewer/technical assessment questions
    elif any(keyword in query_lower for keyword in ['interviewer', 'interview', 'technical', 'skills', 'demonstrate', 'ai/ml', 'engineer']):
        return """👨‍💼 **For AI/ML Interviewers and Technical Leaders:**

**This platform demonstrates comprehensive AI/ML engineering capabilities:**

🧠 **LLM Integration:**
- Local inference with llama.cpp and Mistral 7B
- Custom prompt engineering and response handling
- Context management and conversation flow

📊 **ML Engineering:**
- Automated model selection and training
- Feature engineering and data preprocessing  
- Model evaluation and validation pipelines
- Hyperparameter optimization

⚙️ **MLOps & DevSecOps:**
- Containerized deployment with Docker
- API-first microservices architecture
- Session management and data cleanup
- Air-gapped security model

💻 **Full-Stack Development:**
- Vue.js frontend with real-time features
- FastAPI backend with async processing
- Database integration (ChromaDB, PostgreSQL)
- RESTful API design

🚀 **System Architecture:**
- Scalable microservices design
- Event-driven processing
- Plugin architecture (MCP tools)
- Automated orchestration

**This isn't a tutorial project** - it's a production-ready platform that showcases real-world AI/ML engineering skills.

What specific technical area would you like me to demonstrate?"""

    # Model training questions  
    elif any(keyword in query_lower for keyword in ['model', 'ml', 'machine learning', 'train model', 'prediction']):
        return """📊 **ML Model Training** - Real automated machine learning!

**This demonstrates advanced ML engineering:**

🤖 **Automated ML Pipeline:**
- Feature selection and engineering
- Algorithm comparison (Random Forest, SVM, etc.)
- Hyperparameter optimization
- Cross-validation and metrics evaluation
- Model persistence and deployment

**Enterprise Examples:**
- **Tenant Screening**: Train on historical data to predict lease success
- **Maintenance Prediction**: Forecast equipment failures from work orders  
- **Vendor Performance**: Score vendors on cost, quality, response time
- **Risk Assessment**: Classify applications, properties, or investments

**The Process:**
1. **Upload your CSV data** - any business dataset
2. **I analyze automatically** - data types, patterns, correlations
3. **Select optimal algorithms** - based on problem type and data characteristics
4. **Train and validate** - with proper train/test splits and metrics
5. **Deploy instantly** - ready-to-use prediction API

**Technical Skills Shown:**
- scikit-learn pipeline design
- Feature engineering automation
- Model selection algorithms  
- Performance optimization
- Production deployment

Want to train a model on real data right now?"""

    # Privacy/security questions
    elif any(keyword in query_lower for keyword in ['offline', 'air-gapped', 'privacy', 'secure', 'local', 'no internet']):
        return """🔒 **Enterprise-Grade Privacy & Security**

**Why enterprises choose air-gapped AI:**

🛡️ **Complete Data Isolation:**
- Zero external connections during operation
- All processing happens on your infrastructure
- No data transmission to cloud services
- Perfect for HIPAA, SOX, or classified environments

🔐 **Session Security:**
- Automatic data cleanup on logout
- No persistent storage of sensitive information  
- Memory clearing between sessions
- Audit trails without data retention

🏢 **Enterprise Benefits:**
- **Compliance**: Meet strict data governance requirements
- **Control**: Full oversight of AI processing
- **Cost**: No per-query API fees
- **Speed**: No network latency
- **Reliability**: Works without internet

**Technical Implementation:**
- Local LLM inference with llama.cpp
- Containerized deployment with network isolation
- Encrypted data at rest
- Secure session management
- Docker security hardening

**Perfect for:**
- Healthcare records processing
- Financial data analysis
- Legal document review
- Government operations
- Sensitive R&D workflows

This isn't just "local AI" - it's a complete enterprise privacy architecture."""

    # Demo and showcase questions  
    elif any(keyword in query_lower for keyword in ['demo', 'showcase', 'example', 'see it', 'show me']):
        return """🎬 **Let me show you what I can do live!**

**Choose your demo:**

🔧 **Tool Building Demo** - Watch me create a working Python tool from scratch
📊 **Model Training Demo** - See automated ML on real business data  
🧠 **HTC Learning Demo** - Experience autonomous learning in action
🏢 **Enterprise Scenario** - Property management automation example
👨‍💼 **Technical Deep-Dive** - For AI/ML professionals

**Each demo shows:**
- Real working code generation
- Live model training with metrics
- Actual data processing
- Production-ready deployment

**Not just slides or mockups** - everything works and is immediately usable.

Which demo interests you most? Just type the number or name!"""

    # General capability questions
    elif any(keyword in query_lower for keyword in ['what can you do', 'capabilities', 'features', 'help']):
        return """✨ **I'm Jade - Your Autonomous AI Assistant!** Here's what I can do:

🧠 **Autonomous Learning (HTC):**
• Learn any new task from your uploaded content
• Generate tools, models, and knowledge automatically

🔧 **Tool Creation:**
• Build Python scripts and automation tools
• Create MCP tools for complex workflows

📊 **ML Model Training:**  
• Train models on your data (classification, regression)
• Automatic algorithm selection and optimization

📚 **Document Processing:**
• RAG search through your uploaded documents
• Semantic search and Q&A on your content

💬 **Interactive Chat:**
• Answer questions about your data
• Help with technical problems
• Guide you through the platform

🔒 **Privacy-First:**
• 100% local processing, completely offline
• No external connections or data sharing

Want to try any of these? I'm here to help! Ask me about specific features or click the navigation cards above."""

    return None


@router.post("/jade/query")
async def jade_query(data: JadeQuery) -> Dict[str, Any]:
    """
    Process a query from Jade AI Assistant using local LLM.
    
    Args:
        data: JadeQuery containing the user's query and optional RAG context
        
    Returns:
        Dict containing AI-generated response and metadata
    """
    query = data.query
    context_data = data.context or []
    
    # Build context string from RAG results
    context_text = ""
    if context_data:
        context_parts = []
        for item in context_data:
            if isinstance(item, dict):
                content = item.get('content', str(item))
                context_parts.append(content)
        context_text = "\n\n".join(context_parts)
    
    # Check for specialized responses first
    specialized_response = get_specialized_response(query, data.user_role)
    if specialized_response:
        return {
            "response": specialized_response,
            "execution_time": 0.1,
            "llm_model": "jade-specialized",
            "context_used": False,
            "sources_count": 0,
            "user_role": data.user_role
        }
    
    # Check for tool commands (legacy functionality)
    tool_command = detect_tool_command(query)
    if tool_command:
        return {
            "response": f"🔧 Tool command detected: `{tool_command}`. Tool execution is currently disabled for security.",
            "tool_detected": tool_command,
            "execution_time": 0.1
        }
    
    # Generate AI response using local LLM
    if LLM_AVAILABLE:
        try:
            import time
            start_time = time.time()
            
            # Use the local LLM to generate a response
            if context_text:
                ai_response = generate_answer(query, context_text)
            else:
                # Create a helpful response without context
                ai_response = generate_answer(
                    query, 
                    "You are Jade, an AI assistant for the LinkOps platform. Answer the user's question helpfully and concisely."
                )
            
            execution_time = time.time() - start_time
            
            # Get LLM status for metadata
            llm_runner = get_llm_runner()
            llm_status = llm_runner.get_status()
            
            return {
                "response": ai_response,
                "execution_time": execution_time,
                "llm_model": llm_status.get("model_type", "unknown"),
                "context_used": len(context_data) > 0,
                "sources_count": len(context_data)
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "error": str(e),
                "execution_time": 0.0,
                "llm_model": "error"
            }
    else:
        # Fallback response when LLM is not available
        if context_text:
            return {
                "response": f"I found some relevant information:\n\n{context_text[:500]}{'...' if len(context_text) > 500 else ''}",
                "execution_time": 0.1,
                "llm_model": "fallback",
                "context_used": True
            }
        else:
            return {
                "response": "Hello! I'm Jade, your AI assistant. The local LLM is not currently available, but I can still help you navigate the LinkOps platform.",
                "execution_time": 0.1,
                "llm_model": "fallback",
                "context_used": False
            }


@router.get("/jade/status")
async def jade_status() -> Dict[str, Any]:
    """
    Get the status of the Jade AI Assistant and local LLM.
    
    Returns:
        Dict containing status information
    """
    if LLM_AVAILABLE:
        try:
            llm_runner = get_llm_runner()
            status = llm_runner.get_status()
            return {
                "status": "available",
                "llm_available": True,
                "llm_status": status,
                "version": "1.0.0-local"
            }
        except Exception as e:
            return {
                "status": "error",
                "llm_available": False,
                "error": str(e),
                "version": "1.0.0-local"
            }
    else:
        return {
            "status": "fallback",
            "llm_available": False,
            "message": "Local LLM is not available. Install llama-cpp-python for full functionality.",
            "version": "1.0.0-local"
        }
