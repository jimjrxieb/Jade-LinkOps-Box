#!/usr/bin/env python3
"""
Session Cleanup Middleware
==========================

Automatically cleans up user data on logout or session end for privacy.
"""

import os
import shutil
import logging
from pathlib import Path
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SessionCleanupMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically clean up user session data for privacy.
    """
    
    def __init__(self, app, cleanup_paths: list = None):
        super().__init__(app)
        self.cleanup_paths = cleanup_paths or [
            "htc/intake/uploaded_docs",
            "htc/test_history", 
            "htc/tools",
            "htc/models",
            "db/scratch",
            "rag/uploads"
        ]
        
    async def dispatch(self, request: Request, call_next):
        """Process request and handle cleanup on logout."""
        
        # Check if this is a logout request
        is_logout = (
            request.url.path in ["/auth/logout", "/logout"] or
            request.method == "POST" and "logout" in request.url.path.lower()
        )
        
        response = await call_next(request)
        
        # Perform cleanup on logout
        if is_logout and response.status_code < 400:
            await self._cleanup_user_data(request)
            
        return response
    
    async def _cleanup_user_data(self, request: Request):
        """Clean up all user session data."""
        try:
            base_path = Path(__file__).parent.parent.parent
            
            logger.info("🧹 Starting session cleanup...")
            
            cleanup_count = 0
            
            for cleanup_path in self.cleanup_paths:
                full_path = base_path / cleanup_path
                
                if full_path.exists():
                    if full_path.is_dir():
                        # Clean directory contents but keep the directory
                        for item in full_path.iterdir():
                            try:
                                if item.is_file():
                                    item.unlink()
                                    cleanup_count += 1
                                elif item.is_dir():
                                    shutil.rmtree(item)
                                    cleanup_count += 1
                            except Exception as e:
                                logger.warning(f"Could not delete {item}: {e}")
                    
            # Clean temporary session directories
            temp_session_pattern = base_path / "db" / "scratch" / "session_*"
            for session_dir in temp_session_pattern.parent.glob("session_*"):
                try:
                    shutil.rmtree(session_dir)
                    cleanup_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete session dir {session_dir}: {e}")
            
            # Clean HTC generated files
            htc_patterns = [
                "htc/tools/htc_tool_*.py",
                "htc/models/htc_model_*.joblib", 
                "rag/uploads/htc_knowledge_*.json",
                "db/mcp_tools/htc_learned_*.json"
            ]
            
            for pattern in htc_patterns:
                pattern_path = base_path / pattern
                for file_path in pattern_path.parent.glob(pattern_path.name):
                    try:
                        file_path.unlink()
                        cleanup_count += 1
                    except Exception as e:
                        logger.warning(f"Could not delete {file_path}: {e}")
            
            logger.info(f"✅ Session cleanup completed. Removed {cleanup_count} items.")
            
        except Exception as e:
            logger.error(f"❌ Session cleanup failed: {e}")

def setup_session_cleanup(app):
    """Add session cleanup middleware to the FastAPI app."""
    app.add_middleware(SessionCleanupMiddleware)
    logger.info("🔒 Session cleanup middleware enabled")
    return app