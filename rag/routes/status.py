#!/usr/bin/env python3
"""
Status router for RAG service health checks
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rag"}

@router.get("/status")
async def status():
    """Status endpoint"""
    return {"status": "running", "service": "rag"}