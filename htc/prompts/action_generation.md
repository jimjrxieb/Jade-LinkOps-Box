# MCP Action Generation Prompt Template

You are an expert automation engineer tasked with creating executable MCP (Model Context Protocol) actions based on learned content and user requirements.

## Context
**Task Description**: {task_description}
**Content Analysis**: 
```
{content}
```
**Session ID**: {session_id}
**Tags**: {tags}
**Generated Tools**: {tool_references}

## Instructions

1. **Design an executable action** that automates the user's task
2. **Create MCP tool definition** with proper parameters and metadata
3. **Include error handling and validation**
4. **Provide clear documentation** for the action

## Action Types

### Data Processing Actions
- Automated data analysis and reporting
- File format conversion and validation
- Data quality checks and cleaning
- Batch processing workflows

### Integration Actions  
- API calls and data synchronization
- Database operations and queries
- External service integrations
- Notification and alerting

### Workflow Actions
- Multi-step process automation
- Conditional logic and branching
- Scheduled task execution
- Event-driven processing

### Analysis Actions
- Statistical analysis and reporting
- Machine learning model inference
- Data visualization generation
- Insight extraction and summarization

## Output Format

Generate a complete MCP action definition:

```json
{
  "name": "htc_action_{session_id}",
  "description": "Auto-generated action: {task_description}",
  "category": "htc-learned",
  "version": "1.0.0",
  "metadata": {
    "session_id": "{session_id}",
    "generated_by": "HTC Training",
    "timestamp": "ISO_TIMESTAMP",
    "tags": {tags},
    "complexity": "low|medium|high",
    "estimated_runtime": "seconds"
  },
  "parameters": {
    "input_file": {
      "type": "string",
      "description": "Path to input file",
      "required": true,
      "validation": "file_exists"
    },
    "output_format": {
      "type": "string", 
      "description": "Output format (json, csv, txt)",
      "required": false,
      "default": "json",
      "enum": ["json", "csv", "txt"]
    }
  },
  "execution": {
    "command": "python htc/tools/htc_tool_{session_id}.py",
    "working_directory": ".",
    "timeout": 30,
    "retry_count": 2,
    "environment": {}
  },
  "outputs": {
    "result": {
      "type": "object",
      "description": "Action execution result"
    },
    "metrics": {
      "type": "object", 
      "description": "Performance metrics"
    }
  },
  "error_handling": {
    "on_failure": "log_and_return_error",
    "error_codes": {
      "FILE_NOT_FOUND": "Input file does not exist",
      "INVALID_FORMAT": "Input file format is invalid", 
      "PROCESSING_ERROR": "Error during data processing"
    }
  },
  "documentation": {
    "usage_examples": [
      {
        "description": "Basic usage example",
        "parameters": {
          "input_file": "data.csv"
        }
      }
    ],
    "troubleshooting": [
      {
        "issue": "Common issue description",
        "solution": "How to resolve the issue"
      }
    ]
  }
}
```

## Implementation Guidelines

1. **Robustness**: Include comprehensive error handling
2. **Usability**: Make parameters intuitive and well-documented
3. **Performance**: Optimize for reasonable execution times
4. **Security**: Validate inputs and prevent unsafe operations
5. **Monitoring**: Include logging and metrics collection

## Integration Points

- Reference generated tools from htc/tools/
- Utilize trained models from htc/models/
- Access RAG knowledge for context
- Connect with existing LinkOps services

Generate the complete MCP action definition now: