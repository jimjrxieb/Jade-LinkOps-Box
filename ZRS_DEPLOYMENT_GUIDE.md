# ZRS Property Management AI - Deployment Guide

## Overview

This deployment guide covers the complete ZRS Property Management AI system built on the DEMO-LinkOps platform. The system includes 6 specialized MCP tools, training datasets, Python execution scripts, and Vue.js frontend interfaces for comprehensive property management automation.

## System Components

### 🏢 ZRS MCP Tools (6 tools)
- **send_late_notice**: Late rent notification with legal compliance
- **notify_maintenance**: Maintenance dispatch with priority assignment  
- **vendor_suggest**: AI-powered vendor selection with performance metrics
- **schedule_turnover**: Unit preparation workflow orchestration
- **query_delinquency**: Advanced delinquency analytics with risk assessment
- **broadcast_notice**: Mass tenant communication with delivery tracking

### 🧠 Training System
- **HTC Prompts**: 6 specialized training scenarios in `htc/prompts/`
- **Fine-tuning Dataset**: 40+ property management examples in `htc/datasets/zrs_property_finetune.jsonl`
- **LoRA Training**: `htc/train_jade_zrs.py` for local fine-tuning

### 🔧 Tool Runner Scripts (5 scripts)
- **email_sender.py**: Professional email system with ZRS branding
- **vendor_ranker.py**: Intelligent vendor selection with performance scoring
- **schedule_turnover.py**: Complete unit preparation orchestration
- **query_delinquency.py**: Advanced analytics with risk assessment
- **email_broadcast.py**: Mass communication with delivery tracking

### 🖥️ Frontend Interfaces (2 components)
- **ZRSJadeAssistant.vue**: Complete Jade chat interface with quick actions
- **ZRSMCPTools.vue**: Interactive MCP tool dashboard

## Pre-Deployment Validation

✅ **All validation checks passed:**
- Python syntax validation: PASSED
- JSON configuration validation: PASSED  
- Vue.js component validation: PASSED
- File permissions verification: PASSED
- Helm chart configuration: UPDATED

## Deployment Options

### Option 1: Helm Deployment (Recommended)

```bash
# Deploy with Helm
cd chart/
helm install demo-linkops . --namespace demo-linkops --create-namespace

# Verify deployment
kubectl get pods -n demo-linkops
kubectl get services -n demo-linkops
```

### Option 2: Docker Compose

```bash
# Quick local deployment
docker-compose up -d

# Verify services
docker-compose ps
```

### Option 3: Kubernetes Manual

```bash
# Deploy to existing cluster
kubectl apply -f k8s/
```

## ZRS Tool Configuration

### MCP Tools Location
```
db/mcp_tools/
├── zrs_send_late_notice.json
├── zrs_notify_maintenance.json
├── zrs_vendor_suggest.json
├── zrs_schedule_turnover.json
├── zrs_query_delinquency.json
└── zrs_broadcast_notice.json
```

### Python Execution Scripts
```
tools/
├── email_sender.py (executable)
├── vendor_ranker.py (executable)
├── schedule_turnover.py (executable)
├── query_delinquency.py (executable)
└── email_broadcast.py (executable)
```

### Training Components
```
htc/
├── datasets/zrs_property_finetune.jsonl
├── prompts/zrs_*.json (6 files)
└── train_jade_zrs.py
```

## Configuration

### Helm Values (ZRS Section)
```yaml
zrs:
  enabled: true
  tools:
    mcp_tools_path: /app/db/mcp_tools
    scripts_path: /app/tools
    datasets_path: /app/htc/datasets
    prompts_path: /app/htc/prompts
  
  training:
    enabled: true
    model_name: "microsoft/DialoGPT-small"
    dataset_file: "zrs_property_finetune.jsonl"
    output_path: "/app/models/jade-zrs-property"
    
  tools_config:
    - name: "send_late_notice"
      timeout: 30
      retry_count: 3
    - name: "notify_maintenance" 
      timeout: 30
      retry_count: 2
    # ... (see chart/values.yaml for complete config)
```

## Access Endpoints

### Frontend Access
- **Main Interface**: http://demo.local/
- **ZRS Jade Assistant**: http://demo.local/#/zrs-jade
- **ZRS MCP Tools**: http://demo.local/#/zrs-tools

### API Access
- **Unified API**: http://demo.local/api/
- **ZRS Endpoints**: http://demo.local/zrs/

## Post-Deployment Verification

### 1. Verify ZRS Tools
```bash
# Test MCP tool execution
python3 tools/email_sender.py --tenant_name "Test Tenant" --unit_number "101" --amount_due 1500 --days_late 10

# Check tool configurations
ls -la db/mcp_tools/zrs_*.json
```

### 2. Test Training System
```bash
# Verify training data
python3 -c "import json; data = [json.loads(line) for line in open('htc/datasets/zrs_property_finetune.jsonl')]; print(f'Training examples: {len(data)}')"

# Test training script (optional)
python3 htc/train_jade_zrs.py --help
```

### 3. Frontend Verification
```bash
# Check Vue components
curl -s http://demo.local/ | grep -o "ZRS.*vue" || echo "Frontend accessible"
```

## ZRS Tool Usage Examples

### Send Late Notice
```bash
python3 tools/email_sender.py \
  --tenant_name "Tony Stark" \
  --unit_number "401" \
  --amount_due 2500 \
  --days_late 12
```

### Query Delinquency
```bash
python3 tools/query_delinquency.py \
  --days 15 \
  --building "Building A" \
  --amount 500 \
  --sort days_late
```

### Schedule Turnover
```bash
python3 tools/schedule_turnover.py \
  --unit_number "205" \
  --move_out_date "2025-08-01" \
  --new_lease_date "2025-08-15" \
  --deep_clean
```

## Troubleshooting

### Common Issues

1. **Python Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Denied on Scripts**
   ```bash
   chmod +x tools/*.py
   ```

3. **Missing Training Data**
   ```bash
   # Verify dataset exists
   ls -la htc/datasets/zrs_property_finetune.jsonl
   ```

4. **Helm Deployment Issues**
   ```bash
   helm lint chart/
   helm template demo-linkops chart/ --debug
   ```

### Log Locations
- **Application Logs**: `/app/logs/`
- **Execution History**: `db/logs/execution_history.json`
- **Training Logs**: `models/jade-zrs-property/logs/`

## Security Considerations

- All tools run with limited permissions
- Email credentials stored in environment variables
- ZRS data persistence with proper access controls
- Frontend routes protected with authentication

## Monitoring

### Health Checks
```bash
# API health
curl http://demo.local/api/health

# ZRS tools status
curl http://demo.local/api/zrs/status
```

### Metrics
- Tool execution success rates
- Response times for each ZRS tool
- Training progress and model performance
- User interaction analytics

## Backup and Recovery

### Data Backup
```bash
# Backup ZRS configurations
tar -czf zrs-backup-$(date +%Y%m%d).tar.gz db/mcp_tools/ htc/datasets/ htc/prompts/

# Backup execution logs
cp db/logs/execution_history.json zrs-execution-backup-$(date +%Y%m%d).json
```

### Recovery
```bash
# Restore configurations
tar -xzf zrs-backup-YYYYMMDD.tar.gz

# Restart services
kubectl rollout restart deployment/unified-api -n demo-linkops
```

## Support

For issues specific to ZRS Property Management tools:
1. Check execution logs in `db/logs/`
2. Verify tool configurations in `db/mcp_tools/`
3. Test individual Python scripts directly
4. Review training data format in `htc/datasets/`

For general platform issues, refer to the main DEMO-LinkOps documentation.

---

🏢 **ZRS Property Management AI - Ready for Production**

This system provides a complete offline-capable property management solution with AI-powered tools, automated workflows, and comprehensive training capabilities.