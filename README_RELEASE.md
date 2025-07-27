# 🤖 LinkOps AI Box - Full Version

**A fully offline, local AI assistant with autonomous learning capabilities**

LinkOps AI Box is a complete, air-gapped AI platform featuring Jade, your intelligent assistant, equipped with the revolutionary HTC (Hyperbolic Time Chamber) autonomous learning system. Train Jade on any task, and watch it automatically generate tools, models, and knowledge to execute that task.

## 🌟 Key Features

### 🧠 **Jade AI Assistant**
- **100% Local Processing** - No external API calls, completely offline
- **Advanced RAG** - Semantic search through your documents with ChromaDB
- **Local LLM** - Powered by Mistral 7B via llama.cpp
- **Smart Tool Execution** - MCP-compatible tool runner

### ⚡ **HTC Autonomous Learning System**
- **Learn Any Task** - Upload files and describe what you want Jade to learn
- **Multi-Output Generation**:
  - 🔧 **Tools & Scripts** - Automatically generate Python tools
  - 🤖 **ML Models** - Train classification/regression models from data
  - 📚 **Knowledge Base** - Create searchable RAG entries
  - ⚡ **Executable Actions** - Generate MCP actions for automation

### 🔒 **Privacy & Security**
- **Air-Gapped Operation** - Works completely offline
- **Session Auto-Cleanup** - All user data deleted on logout
- **Local Data Storage** - Everything stays on your machine
- **No Telemetry** - Zero data collection or external connections

### 🛠️ **Enterprise-Ready**
- **Docker Deployment** - Easy containerized setup
- **Scalable Architecture** - Microservices-based design
- **API-First** - RESTful APIs for all functionality
- **Developer-Friendly** - Full documentation and CLI tools

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM (16GB recommended)
- 10GB+ storage space

### Installation

1. **Extract the AI Box**
   ```bash
   unzip LinkOps-AI-Box-v1.0.0.zip
   cd DEMO-LinkOps
   ```

2. **Download AI Model** (First time only)
   ```bash
   cd rag/llm_weights
   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O mistral.gguf
   cd ../..
   ```

3. **Start the AI Box**
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

4. **Access Jade**
   - Open: [http://localhost:3000](http://localhost:3000)
   - Login: `linkops-demo` / `demo123`

### 🧪 Offline Test

```bash
# Turn off network to verify offline operation
sudo nmcli networking off  # Linux
# Or disconnect WiFi manually

# Verify services are running
curl -s localhost:9000/health && echo "✅ Backend online"
curl -s localhost:3000 | grep "LinkOps" && echo "✅ Frontend online"
```

## 📋 Usage Guide

### 🎯 **Getting Started with Jade**

1. **Chat Interface** - Ask questions, get help with tasks
2. **Document Upload** - Upload files for Jade to learn from
3. **HTC Training** - Train Jade on new tasks autonomously

### 🧠 **HTC Autonomous Learning**

1. **Navigate to HTC Trainer** from the dashboard
2. **Describe Your Task** - What do you want Jade to learn?
3. **Upload Training Content** - CSV, JSON, text, code, docs
4. **Select Outputs** - Choose what to generate:
   - Tools for automation
   - ML models for predictions
   - Knowledge for future queries
   - Actions for workflow automation
5. **Start Training** - Watch Jade learn and create assets automatically

### 📝 **Example Training Sessions**

#### Data Analysis Task
```
Task: "Analyze customer data and generate risk scores"
Files: customer_data.csv
Outputs: Tool + Model + RAG
Result: Python analysis tool + trained risk model + searchable knowledge
```

#### API Documentation Learning
```
Task: "Learn API documentation and create integration tools"
Files: api_docs.md, examples.json
Outputs: Tool + RAG + Action
Result: API client tool + knowledge base + automated actions
```

#### Process Automation
```
Task: "Automate data processing workflow"
Files: process_docs.txt, sample_data.csv
Outputs: Tool + Action
Result: Automation script + executable workflow
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Unified API   │    │   HTC System    │
│   (Vue3)        │◄───┤   (FastAPI)     │◄───┤   (Training)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG System    │    │   ML Models     │    │   Sync Engine   │
│   (ChromaDB)    │    │   (Sklearn)     │    │   (File Sync)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
┌─────────────────┐
│   Local LLM     │
│   (llama.cpp)   │
└─────────────────┘
```

## 🔧 Development

### CLI Tools

```bash
# HTC CLI for testing
cd htc
python cli.py status                    # Check system status
python cli.py train "task" file.csv     # Train on data
python cli.py history                   # View training history
python cli.py assets                    # List generated assets
```

### API Endpoints

- **Frontend**: `http://localhost:3000`
- **API Docs**: `http://localhost:9000/docs`
- **Health Check**: `http://localhost:9000/health`
- **HTC API**: `http://localhost:9000/htc-trainer/*`
- **RAG API**: `http://localhost:9000/rag/*`
- **Jade Chat**: `http://localhost:9000/jade/*`

### Directory Structure

```
DEMO-LinkOps/
├── frontend/          # Vue3 + Tailwind frontend
├── unified-api/       # FastAPI backend services
├── rag/              # ChromaDB + local LLM
├── htc/              # HTC autonomous learning system
├── sync_engine/      # File synchronization
├── db/               # Local databases and logs
├── ml_models/        # ML training components
└── docker-compose.yml # Container orchestration
```

## 🔒 Security & Privacy

### Data Protection
- ✅ **No External Connections** - Completely air-gapped
- ✅ **Local Processing** - All AI inference happens locally
- ✅ **Session Isolation** - User data cleaned on logout
- ✅ **No Telemetry** - Zero data collection

### Authentication
- Simple demo credentials for local testing
- Session-based authentication
- Automatic session cleanup

## 📊 System Requirements

### Minimum
- **CPU**: 4+ cores
- **RAM**: 8GB
- **Storage**: 10GB
- **OS**: Docker-compatible (Linux, macOS, Windows)

### Recommended
- **CPU**: 8+ cores
- **RAM**: 16GB
- **Storage**: 20GB
- **GPU**: Optional (for faster inference)

## 🛠️ Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check Docker resources
docker system df
docker system prune  # If needed
```

**Frontend can't connect**
```bash
# Verify backend is running
curl localhost:9000/health
# Check port conflicts
netstat -tulpn | grep :3000
```

**AI model not found**
```bash
# Download model manually
cd rag/llm_weights
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O mistral.gguf
```

**HTC training fails**
```bash
# Check HTC system status
cd htc
python cli.py status
# View logs
docker compose logs unified-api
```

### Performance Optimization

**For better performance:**
- Increase Docker memory allocation
- Use GPU acceleration if available
- Use smaller model quantization for faster inference
- Close unnecessary applications to free RAM

## 📈 Version History

- **v1.0.0** - Initial release with HTC autonomous learning system
  - Complete offline AI assistant
  - HTC autonomous learning and tool generation
  - Local LLM integration (Mistral 7B)
  - RAG system with ChromaDB
  - Session auto-cleanup
  - Docker deployment

## 🤝 Support

This is a demonstration system. For technical questions:
- Check the API documentation at `/docs`
- Review logs with `docker compose logs`
- Use the built-in CLI tools for debugging

## 📄 License

This is demonstration software for evaluation purposes.

---

**🎯 LinkOps AI Box - Where AI Learns What You Teach**

*Experience the future of autonomous AI learning with Jade and the HTC system.*