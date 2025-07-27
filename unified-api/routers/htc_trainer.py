#!/usr/bin/env python3
"""
HTC Trainer API Router
======================

API endpoints for the HTC (Human-Trainable Computer) autonomous learning system.
Allows training Jade on new tasks and content.
"""

import os
import sys
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import tempfile
import shutil
from pathlib import Path

# Add HTC module to path
htc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'htc')
if htc_path not in sys.path:
    sys.path.append(htc_path)

try:
    from logic.htc_trainer import get_htc_trainer, train_on_task
    HTC_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import HTC trainer: {e}")
    HTC_AVAILABLE = False

router = APIRouter()

class HTCTrainingRequest(BaseModel):
    task_description: str
    files: List[str]
    desired_outputs: List[str]  # ["tool", "model", "rag", "action"]
    tags: List[str]
    user_context: Optional[str] = None

class HTCTrainingResponse(BaseModel):
    session_id: str
    status: str
    task: str
    timestamp: str
    files_processed: List[str]
    outputs_requested: List[str]
    generated: Dict[str, Any]
    errors: List[str]
    execution_time: Optional[float] = None

@router.post("/htc/train", response_model=HTCTrainingResponse)
async def train_htc(data: HTCTrainingRequest) -> HTCTrainingResponse:
    """
    Train the HTC system on a new task with uploaded content.
    
    Args:
        data: Training request with task description and file references
        
    Returns:
        Training session results with generated assets
    """
    if not HTC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HTC training system is not available. Check server configuration."
        )
    
    try:
        import time
        start_time = time.time()
        
        # Validate inputs
        if not data.task_description.strip():
            raise HTTPException(status_code=400, detail="Task description is required")
        
        if not data.files:
            raise HTTPException(status_code=400, detail="At least one file is required")
        
        valid_outputs = ["tool", "model", "rag", "action"]
        invalid_outputs = [o for o in data.desired_outputs if o not in valid_outputs]
        if invalid_outputs:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid output types: {invalid_outputs}. Valid: {valid_outputs}"
            )
        
        # Execute training
        trainer = get_htc_trainer()
        results = await trainer.train_on_task(
            task_description=data.task_description,
            files=data.files,
            desired_outputs=data.desired_outputs,
            tags=data.tags,
            user_context=data.user_context
        )
        
        execution_time = time.time() - start_time
        results["execution_time"] = execution_time
        
        return HTCTrainingResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.post("/htc/upload")
async def upload_training_files(
    files: List[UploadFile] = File(...),
    task_description: str = Form(...)
) -> Dict[str, Any]:
    """
    Upload files for HTC training.
    
    Args:
        files: List of files to upload
        task_description: Description of the training task
        
    Returns:
        Upload results with file references
    """
    if not HTC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HTC training system is not available"
        )
    
    try:
        trainer = get_htc_trainer()
        uploaded_files = []
        
        for file in files:
            # Validate file
            if not file.filename:
                continue
                
            # Save file to intake directory
            file_path = trainer.intake_path / file.filename
            
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": file_path.stat().st_size,
                "path": str(file_path)
            })
        
        return {
            "status": "success",
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "task_description": task_description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/htc/history")
async def get_training_history() -> Dict[str, Any]:
    """
    Get HTC training session history.
    
    Returns:
        List of past training sessions
    """
    if not HTC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HTC training system is not available"
        )
    
    try:
        trainer = get_htc_trainer()
        history = trainer.get_training_history()
        
        return {
            "status": "success",
            "sessions": history,
            "total_sessions": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/htc/assets")
async def get_generated_assets() -> Dict[str, Any]:
    """
    Get list of all generated HTC assets.
    
    Returns:
        Lists of generated tools, models, and session files
    """
    if not HTC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HTC training system is not available"
        )
    
    try:
        trainer = get_htc_trainer()
        assets = trainer.get_generated_assets()
        
        return {
            "status": "success",
            "assets": assets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assets: {str(e)}")

@router.get("/htc/status")
async def get_htc_status() -> Dict[str, Any]:
    """
    Get HTC system status and health.
    
    Returns:
        System status and configuration info
    """
    return {
        "status": "available" if HTC_AVAILABLE else "unavailable",
        "htc_available": HTC_AVAILABLE,
        "features": {
            "tool_generation": True,
            "model_training": True,
            "rag_knowledge": True,
            "mcp_actions": True
        },
        "version": "1.0.0",
        "description": "Human-Trainable Computer - Autonomous Learning System"
    }

@router.delete("/htc/session/{session_id}")
async def delete_training_session(session_id: str) -> Dict[str, Any]:
    """
    Delete a specific training session and its generated assets.
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        Deletion status
    """
    if not HTC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HTC training system is not available"
        )
    
    try:
        trainer = get_htc_trainer()
        
        # Delete session file
        session_file = trainer.test_history_path / f"session_{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        
        # Delete generated assets
        deleted_assets = []
        
        # Delete tools
        tool_file = trainer.tools_path / f"htc_tool_{session_id}.py"
        if tool_file.exists():
            tool_file.unlink()
            deleted_assets.append(f"tool: {tool_file.name}")
        
        # Delete models
        model_file = trainer.models_path / f"htc_model_{session_id}.joblib"
        if model_file.exists():
            model_file.unlink()
            deleted_assets.append(f"model: {model_file.name}")
        
        # Delete RAG entries
        rag_file = trainer.base_path.parent / "rag" / "uploads" / f"htc_knowledge_{session_id}.json"
        if rag_file.exists():
            rag_file.unlink()
            deleted_assets.append(f"rag: {rag_file.name}")
        
        # Delete MCP actions
        mcp_file = trainer.base_path.parent / "db" / "mcp_tools" / f"htc_learned_{session_id}.json"
        if mcp_file.exists():
            mcp_file.unlink()
            deleted_assets.append(f"mcp: {mcp_file.name}")
        
        return {
            "status": "success",
            "session_id": session_id,
            "deleted_assets": deleted_assets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")