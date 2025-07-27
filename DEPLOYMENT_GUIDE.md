# 🚀 Jade AI Box - Deployment Guide

## Quick Start (5 Minutes)

### **Option 1: Lightning Fast Deploy**
```bash
./quick-deploy.sh
```
- ✅ Downloads AI model automatically
- ✅ Builds and starts all services  
- ✅ Ready in under 5 minutes
- ✅ Perfect for demos and testing

### **Option 2: Production Deploy**
```bash
./deploy.sh
```
- ✅ Full production configuration
- ✅ Security hardening enabled
- ✅ Health checks and monitoring
- ✅ Backup and recovery setup

---

## Deployment Options

### 🏠 **Local Development**
```bash
# Standard development setup
docker compose up -d

# With logs
docker compose up --build
```

### 🌐 **Local Production**
```bash
# Full production stack locally
./deploy.sh

# Custom domain
DOMAIN=demo.local ./deploy.sh
```

### ☁️ **Cloud Deployment**

#### **DigitalOcean Droplet**
```bash
# 1. Create droplet (4GB RAM minimum)
# 2. SSH into droplet
# 3. Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Clone and deploy
git clone [your-repo]
cd DEMO-LinkOps
./deploy.sh
```

#### **AWS EC2**
```bash
# Use t3.medium or larger (2 vCPU, 4GB RAM)
# Amazon Linux 2 recommended

# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy
./deploy.sh
```

#### **Kubernetes (any cloud)**
```bash
# Apply the cloud deployment
kubectl apply -f deploy-cloud.yml

# Update domains in the ingress
kubectl edit ingress linkops-ingress -n linkops
```

---

## System Requirements

### **Minimum (Demo/Testing)**
- **CPU**: 2 cores
- **RAM**: 4GB  
- **Storage**: 8GB
- **Network**: Basic internet for initial model download

### **Recommended (Production)**
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 20GB+ (SSD preferred)
- **Network**: Stable connection for updates

### **Cloud Instance Sizes**
- **AWS**: t3.medium or larger
- **DigitalOcean**: 4GB droplet or larger  
- **GCP**: e2-medium or larger
- **Azure**: B2s or larger

---

## Configuration Options

### **Environment Variables**
```bash
# Domain configuration
DOMAIN=your-domain.com

# SSL/HTTPS
ENABLE_SSL=true

# Model configuration  
LLM_MODEL_PATH=rag/llm_weights/mistral.gguf
LLM_TEMPERATURE=0.1

# Security
AUTO_CLEANUP_ON_LOGOUT=true
SESSION_TIMEOUT=3600

# Performance
ENABLE_CACHING=true
MAX_UPLOAD_SIZE=100MB
```

### **Model Options**
```bash
# High Quality (4.1GB) - Recommended
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O rag/llm_weights/mistral.gguf

# Fast/Smaller (2.9GB) - Good for demos
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q2_K.gguf -O rag/llm_weights/mistral.gguf

# Tiny (1.1GB) - Testing only
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q2_K.gguf -O rag/llm_weights/mistral.gguf
```

---

## SSL/HTTPS Setup

### **Option 1: Cloudflare (Recommended)**
1. Point your domain to your server IP
2. Enable Cloudflare proxy
3. Set SSL mode to "Full"
4. Jade will be available at `https://your-domain.com`

### **Option 2: Let's Encrypt**
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx config to use SSL
# Restart with SSL enabled
ENABLE_SSL=true ./deploy.sh
```

### **Option 3: Reverse Proxy**
```nginx
# nginx config
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:9000/;
    }
}
```

---

## Monitoring & Maintenance

### **Health Checks**
```bash
# Check all services
curl localhost:9000/health

# Check frontend
curl localhost:3000/health

# Check Jade AI
curl -X POST localhost:9000/jade/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'
```

### **Logs**
```bash
# View all logs
docker compose logs -f

# Specific service logs
docker compose logs -f unified-api
docker compose logs -f frontend

# System logs
journalctl -u docker
```

### **Performance Monitoring**
```bash
# Container resource usage
docker stats

# System resources
htop
df -h
free -h

# Network status
netstat -tulpn | grep :3000
netstat -tulpn | grep :9000
```

### **Updates**
```bash
# Update platform
git pull
./deploy.sh

# Update just containers
docker compose pull
docker compose up -d
```

---

## Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```bash
# Find what's using the port
sudo lsof -i :3000
sudo lsof -i :9000

# Kill the process
sudo kill -9 <PID>

# Or use different ports
PORT=3001 ./deploy.sh
```

#### **Out of Memory**
```bash
# Check memory usage
free -h
docker stats

# Increase swap (if needed)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **Model Download Failed**
```bash
# Download manually
cd rag/llm_weights
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -O mistral.gguf

# Verify file
ls -lh mistral.gguf
file mistral.gguf
```

#### **Services Won't Start**
```bash
# Check Docker daemon
sudo systemctl status docker
sudo systemctl start docker

# Check logs
docker compose logs

# Reset everything
docker compose down -v
docker system prune -af
./deploy.sh
```

#### **Jade Not Responding**
```bash
# Check backend health
curl localhost:9000/health

# Check model file
ls -la rag/llm_weights/mistral.gguf

# Restart backend
docker compose restart unified-api
```

---

## Security Considerations

### **Production Security**
- ✅ Change default passwords
- ✅ Use HTTPS in production
- ✅ Configure firewall rules
- ✅ Regular security updates
- ✅ Monitor access logs

### **Data Privacy**
- ✅ All processing happens locally
- ✅ No external API calls
- ✅ Session auto-cleanup enabled
- ✅ Data encryption at rest (optional)

### **Network Security**
```bash
# Firewall setup (Ubuntu/Debian)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Only allow specific IPs (optional)
sudo ufw allow from YOUR.IP.ADDRESS to any port 3000
```

---

## Backup & Recovery

### **Backup Important Data**
```bash
# Create backup
mkdir -p backups/$(date +%Y%m%d)

# Backup user data
cp -r htc/test_history/ backups/$(date +%Y%m%d)/
cp -r db/ backups/$(date +%Y%m%d)/

# Backup configuration
cp .env.production backups/$(date +%Y%m%d)/
```

### **Restore from Backup**
```bash
# Stop services
docker compose down

# Restore data
cp -r backups/20240101/* ./

# Restart
./deploy.sh
```

---

## Performance Optimization

### **For Better Performance**
```bash
# Use SSD storage
# Increase RAM allocation
# Use faster CPU
# Enable caching
ENABLE_CACHING=true ./deploy.sh

# Optimize Docker
# Add to /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## Getting Help

### **Documentation**
- API Docs: `http://your-domain:9000/docs`
- Health Check: `http://your-domain:9000/health`
- Frontend: `http://your-domain:3000`

### **Support**
- Check logs first: `docker compose logs`
- Verify requirements are met
- Try the troubleshooting steps above
- Create GitHub issue with logs and system info

---

**🎉 Your Jade AI Box is ready to demonstrate the future of adaptive AI!**