#!/usr/bin/env python3
"""
Prompt editor router for RAG service
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/prompt-editor")
async def get_prompt_editor():
    """Get prompt editor interface"""
    return {"status": "ready", "editor": "prompt_editor"}

@router.post("/prompt-editor")
async def update_prompt(prompt_data: dict):
    """Update prompt configuration"""
    return {"status": "updated", "data": prompt_data}