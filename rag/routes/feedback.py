#!/usr/bin/env python3
"""
Feedback router for RAG service
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("/feedback")
async def submit_feedback(feedback: dict):
    """Submit feedback endpoint"""
    return {"status": "received", "feedback": feedback}