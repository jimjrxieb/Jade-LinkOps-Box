# LinkOps AI Box v1.0.0 - HTC Autonomous Learning Release

## 🎉 Major Release: Introducing HTC (Hyperbolic Time Chamber)

LinkOps AI Box v1.0.0 introduces revolutionary **autonomous learning capabilities** through the HTC system. Now Jade can learn any new task from your uploaded content and automatically generate the tools, models, and knowledge needed to execute that task.

## 🌟 What's New in v1.0.0

### 🧠 **HTC Autonomous Learning System**
- **Learn Any Task**: Upload files, describe what you want Jade to learn, and watch it automatically generate assets
- **Multi-Output Generation**: 
  - 🔧 **Python Tools & Scripts** for automation
  - 🤖 **ML Models** for predictions and analysis  
  - 📚 **Knowledge Entries** for RAG search
  - ⚡ **Executable Actions** for workflow automation
- **Smart Analysis**: Automatically detects data types and selects appropriate modeling approaches
- **Web Interface**: Beautiful Vue.js UI for training sessions with real-time progress

### 🔒 **Enhanced Privacy & Security**
- **Session Auto-Cleanup**: All user data automatically deleted on logout
- **100% Air-Gapped**: Complete offline operation with no external dependencies
- **Local LLM Integration**: Mistral 7B running locally via llama.cpp
- **Zero Telemetry**: No data collection or external connections

### 🛠️ **Developer Experience**
- **CLI Tools**: Command-line interface for HTC training and management
- **API-First**: RESTful endpoints for all HTC functionality
- **Docker Deployment**: Easy containerized setup
- **Comprehensive Documentation**: Full usage guides and examples

### 🎯 **Core Platform Features**
- **Jade AI Assistant**: Smart local AI with RAG capabilities
- **Document Processing**: Support for CSV, JSON, text, code, and documentation
- **Vector Search**: ChromaDB-powered semantic search
- **Tool Execution**: MCP-compatible tool runner
- **ML Training**: Automated model training from CSV data

## 📦 Download & Installation

### Quick Start
1. Download `LinkOps-AI-Box-v1.0.0.zip`
2. Extract and run:
   ```bash
   cd DEMO-LinkOps
   docker compose build --no-cache
   docker compose up -d
   ```
3. Open http://localhost:3000
4. Login: `linkops-demo` / `demo123`

### First-Time Setup
Download the AI model (4.1GB):
```bash
cd rag/llm_weights
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O mistral.gguf
```

## 🧪 Testing Offline Capability

Run the included test script to verify complete offline operation:
```bash
./test_offline.sh
```

This will:
- Disable network connectivity
- Start all services  
- Verify endpoints are responding
- Confirm air-gapped operation

## 📋 Example Use Cases

### Data Analysis Training
```
Task: "Analyze customer data and generate risk scores"
Upload: customer_data.csv
Result: Python analysis tool + trained risk model + searchable knowledge
```

### API Documentation Learning  
```
Task: "Learn API documentation and create integration tools"
Upload: api_docs.md, examples.json
Result: API client tool + knowledge base + automated actions
```

### Process Automation
```
Task: "Automate data processing workflow"  
Upload: process_docs.txt, sample_data.csv
Result: Automation script + executable workflow
```

## 🏗️ Technical Architecture

- **Frontend**: Vue 3 + Tailwind CSS + Pinia
- **Backend**: FastAPI with microservices architecture
- **AI Engine**: Local Mistral 7B via llama.cpp
- **Vector DB**: ChromaDB for semantic search
- **ML Training**: scikit-learn with automated model selection
- **Deployment**: Docker Compose for easy setup

## 📊 System Requirements

### Minimum
- CPU: 4+ cores
- RAM: 8GB  
- Storage: 10GB
- OS: Docker-compatible

### Recommended  
- CPU: 8+ cores
- RAM: 16GB
- Storage: 20GB
- GPU: Optional for faster inference

## 🔧 API Endpoints

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:9000/docs
- **Health Check**: http://localhost:9000/health
- **HTC Training**: http://localhost:9000/htc-trainer/*
- **Jade Chat**: http://localhost:9000/jade/*
- **RAG Search**: http://localhost:9000/rag/*

## 🧠 HTC CLI Tools

```bash
cd htc
python cli.py status                    # System status
python cli.py train "task" file.csv     # Train on data  
python cli.py history                   # Training history
python cli.py assets                    # Generated assets
```

## 🔒 Privacy Features

✅ **No External Connections** - Completely air-gapped  
✅ **Local Processing** - All AI inference happens locally  
✅ **Session Isolation** - User data cleaned on logout  
✅ **No Telemetry** - Zero data collection  

## 🛠️ Troubleshooting

**Services won't start**: Check Docker resources with `docker system df`  
**Frontend can't connect**: Verify backend with `curl localhost:9000/health`  
**AI model not found**: Download model to `rag/llm_weights/mistral.gguf`  
**HTC training fails**: Check status with `cd htc && python cli.py status`  

## 📈 What's Next

Future releases will include:
- GPU acceleration support
- Additional model formats (ONNX, PyTorch)
- Advanced workflow automation
- Enhanced visualization tools
- Enterprise deployment options

## 🤝 Support & Feedback

This is demonstration software for evaluation. For technical questions:
- Check API documentation at `/docs`
- Review logs with `docker compose logs`
- Use built-in CLI tools for debugging

---

**🎯 LinkOps AI Box - Where AI Learns What You Teach**

Experience the future of autonomous AI learning with Jade and the revolutionary HTC system.

### Checksums
- **LinkOps-AI-Box-v1.0.0.zip**: `sha256: [CHECKSUM_HERE]`
- **Size**: ~500MB (excluding AI model)

### Support
- **Compatible OS**: Linux, macOS, Windows (with Docker)
- **Docker Version**: 20.10+
- **Docker Compose**: 2.0+