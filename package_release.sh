#!/bin/bash

echo "📦 LinkOps AI Box - Release Packaging Script"
echo "============================================="

# Get version
VERSION=$(cat VERSION_RELEASE)
PACKAGE_NAME="LinkOps-AI-Box-v${VERSION}"
ARCHIVE_NAME="${PACKAGE_NAME}.zip"

echo "🏷️  Version: $VERSION"
echo "📁 Package: $PACKAGE_NAME"

# Create temporary packaging directory
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

echo ""
echo "📋 Preparing package structure..."

# Create package directory
mkdir -p "$PACKAGE_DIR"

# Copy core directories and files
echo "📂 Copying core components..."
cp -r frontend/ "$PACKAGE_DIR/"
cp -r unified-api/ "$PACKAGE_DIR/"
cp -r rag/ "$PACKAGE_DIR/"
cp -r htc/ "$PACKAGE_DIR/"
cp -r sync_engine/ "$PACKAGE_DIR/"
cp -r db/ "$PACKAGE_DIR/"
cp -r ml_models/ "$PACKAGE_DIR/"

# Copy configuration files
echo "📄 Copying configuration files..."
cp docker-compose.yml "$PACKAGE_DIR/"
cp Dockerfile "$PACKAGE_DIR/"
cp README_RELEASE.md "$PACKAGE_DIR/README.md"
cp VERSION_RELEASE "$PACKAGE_DIR/VERSION"
cp test_offline.sh "$PACKAGE_DIR/"

# Create .env template
echo "📝 Creating environment template..."
cat > "$PACKAGE_DIR/.env.template" << 'EOF'
# LinkOps AI Box Environment Configuration
# Copy this file to .env and customize as needed

# Application Settings
NODE_ENV=production
ENVIRONMENT=demo

# Demo Credentials (change for production)
DEMO_USERNAME=linkops-demo
DEMO_PASSWORD=demo123

# AI Model Settings
LLM_MODEL_PATH=rag/llm_weights/mistral.gguf
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=512

# Database Settings
CHROMA_PERSIST_DIRECTORY=rag/chroma_db
POSTGRES_DB=linkops_demo
POSTGRES_USER=linkops
POSTGRES_PASSWORD=demo123

# Security Settings (for production)
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Resource Limits
MAX_UPLOAD_SIZE=100MB
SESSION_TIMEOUT=3600

# Cleanup Settings
AUTO_CLEANUP_ON_LOGOUT=true
CLEANUP_TEMP_FILES=true
EOF

# Clean up unnecessary files
echo "🧹 Cleaning up unnecessary files..."
find "$PACKAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove large model weights (user downloads separately)
rm -f "$PACKAGE_DIR/rag/llm_weights/"*.gguf 2>/dev/null || true

# Create model download instruction
cat > "$PACKAGE_DIR/rag/llm_weights/DOWNLOAD_MODEL.md" << 'EOF'
# AI Model Download Instructions

This directory should contain the Mistral 7B model file for local AI inference.

## Download Command

```bash
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O mistral.gguf
```

## Alternative Models (Optional)

### Smaller Model (2.9GB - Faster)
```bash
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q2_K.gguf -O mistral.gguf
```

### Larger Model (7.2GB - Better Quality)  
```bash
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q8_0.gguf -O mistral.gguf
```

## Model Requirements

- File must be named `mistral.gguf`
- Place in this directory: `rag/llm_weights/`
- Size: 4.1GB (Q4_K_M recommended)

The system will automatically detect and load the model when services start.
EOF

# Set execute permissions
chmod +x "$PACKAGE_DIR/test_offline.sh"
chmod +x "$PACKAGE_DIR/htc/cli.py"

# Create release notes
echo "📄 Creating release information..."
cat > "$PACKAGE_DIR/RELEASE_NOTES.md" << EOF
# LinkOps AI Box v${VERSION} - Release Notes

## 🎉 HTC Autonomous Learning Release

This release introduces the revolutionary HTC (Hyperbolic Time Chamber) autonomous learning system, transforming Jade from a simple AI assistant into a self-training, self-enhancing AI platform.

## 🚀 Quick Start

1. **Extract Package**
   \`\`\`bash
   unzip ${ARCHIVE_NAME}
   cd ${PACKAGE_NAME}
   \`\`\`

2. **Download AI Model**
   \`\`\`bash
   cd rag/llm_weights
   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O mistral.gguf
   cd ../..
   \`\`\`

3. **Start Services**
   \`\`\`bash
   docker compose build --no-cache
   docker compose up -d
   \`\`\`

4. **Access Jade**
   - URL: http://localhost:3000
   - Login: linkops-demo / demo123

## 🧪 Test Offline Mode

\`\`\`bash
./test_offline.sh
\`\`\`

## 📦 Package Contents

- **frontend/**: Vue.js web interface
- **unified-api/**: FastAPI backend services  
- **rag/**: RAG system with ChromaDB
- **htc/**: HTC autonomous learning system
- **sync_engine/**: File synchronization
- **ml_models/**: ML training components
- **docker-compose.yml**: Service orchestration
- **test_offline.sh**: Offline capability test

## 🔒 Privacy Features

✅ 100% Local Processing  
✅ No External Connections  
✅ Session Auto-Cleanup  
✅ Air-Gapped Operation  

Built on $(date +"%Y-%m-%d")
Release v${VERSION}
EOF

# Calculate package size
echo ""
echo "📊 Package Statistics:"
PACKAGE_SIZE=$(du -sh "$PACKAGE_DIR" | cut -f1)
FILE_COUNT=$(find "$PACKAGE_DIR" -type f | wc -l)
echo "   Size: $PACKAGE_SIZE"
echo "   Files: $FILE_COUNT"

# Create archive
echo ""
echo "🗜️  Creating release archive..."
cd "$TEMP_DIR"
zip -r "$ARCHIVE_NAME" "$PACKAGE_NAME/" -x "*.DS_Store" "*/node_modules/*" "*/__pycache__/*" "*.pyc"

# Move to current directory
mv "$ARCHIVE_NAME" "$(pwd)/../$ARCHIVE_NAME"
FINAL_SIZE=$(du -sh "../$ARCHIVE_NAME" | cut -f1)

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Package created successfully!"
echo "📦 Archive: $ARCHIVE_NAME"
echo "📏 Size: $FINAL_SIZE"
echo ""

# Generate checksums
echo "🔐 Generating checksums..."
cd ..
sha256sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.sha256"
md5sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.md5"

echo "📋 Release files:"
echo "   - $ARCHIVE_NAME"
echo "   - ${ARCHIVE_NAME}.sha256"
echo "   - ${ARCHIVE_NAME}.md5"

echo ""
echo "🎯 Release package ready for distribution!"
echo ""
echo "📝 Next steps:"
echo "   1. Test the package on a clean system"
echo "   2. Upload to release platform"
echo "   3. Update documentation with download links"
echo "   4. Announce the release"