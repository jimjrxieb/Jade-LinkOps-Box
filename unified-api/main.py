#!/usr/bin/env python3
"""
Unified API Router - Single Backend for All Services
===================================================

This service provides a unified API gateway that routes requests to all
microservices (ML Creator, Agent Creator, Pipeline, RAG) through a single
endpoint on port 9000.
"""

import logging
import time
from datetime import datetime

from dependencies import require_full
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import session cleanup middleware
from middleware.session_cleanup import setup_session_cleanup

# Import routers from each service
from routers import (
    agent_builder,
    agent_creator,
    auth,
    auto_runner,
    demo_sync,
    executor,
    htc,
    htc_trainer,
    jade_assistant,
    mcp_tool,
    ml_builder,
    ml_models,
    model_creator,
    pipeline,
    property_management,
    rag,
    sync_engine,
    train_model,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DEMO-LinkOps API",
    description="Secure AI Platform - Unified Backend for ML, Agents, Pipeline, and RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"])

# Add session cleanup middleware for privacy
setup_session_cleanup(app)

# Include routers from each service
app.include_router(
    model_creator.router, prefix="/model-creator", tags=["ML Model Creator"]
)

app.include_router(
    agent_creator.router, prefix="/agent-creator", tags=["AI Agent Creator"]
)

app.include_router(pipeline.router, prefix="/pipeline", tags=["Training Pipeline"])

app.include_router(rag.router, prefix="/rag", tags=["RAG Search"])

app.include_router(ml_builder.router, prefix="/ml-builder", tags=["ML Model Builder"])

app.include_router(
    agent_builder.router, prefix="/agent-builder", tags=["Agent Builder"]
)

app.include_router(train_model.router, prefix="/train-model", tags=["Model Training"])

app.include_router(mcp_tool.router, prefix="/mcp-tool", tags=["MCP Tool Creator"])

app.include_router(executor.router, prefix="/executor", tags=["MCP Tool Executor"])

app.include_router(htc.router, prefix="/htc", tags=["HTC Document Memory"])

app.include_router(htc_trainer.router, prefix="/htc-trainer", tags=["HTC Autonomous Learning"])

app.include_router(auto_runner.router, prefix="/auto-runner", tags=["Auto Tool Runner"])

app.include_router(demo_sync.router, tags=["Demo Sync"])

app.include_router(ml_models.router, tags=["Enhanced ML Models"])

app.include_router(auth.router, prefix="/auth", tags=["auth"])

app.include_router(sync_engine.router, tags=["Sync Engine"])
app.include_router(jade_assistant.router, tags=["Jade Assistant"])
app.include_router(property_management.router, prefix="/property", tags=["ZRS Property Management"])


# Example of protecting a full-access endpoint
@app.post("/train_model", dependencies=[Depends(require_full)])
async def train_model():
    return {"message": "Model training started"}


@app.post("/ml_builder", dependencies=[Depends(require_full)])
async def ml_builder():
    return {"message": "ML builder accessed"}


# Global middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(f"🔍 {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"✅ {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)"
    )

    return response


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "LinkOps Unified API",
        "version": "1.0.0",
        "description": "Secure AI Platform Backend",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "model_creator": "/model-creator",
            "agent_creator": "/agent-creator",
            "pipeline": "/pipeline",
            "rag": "/rag",
            "ml_builder": "/ml-builder",
            "agent_builder": "/agent-builder",
            "train_model": "/train-model",
            "mcp_tool": "/mcp-tool",
            "executor": "/executor",
            "htc": "/htc",
            "htc_trainer": "/htc-trainer",
            "docs": "/docs",
            "health": "/health",
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {},
    }

    # Check each service
    try:
        # Model Creator health
        model_health = await model_creator.health_check()
        health_status["services"]["model_creator"] = model_health
    except Exception as e:
        health_status["services"]["model_creator"] = {
            "status": "error",
            "error": str(e),
        }

    try:
        # Agent Creator health
        agent_health = await agent_creator.health_check()
        health_status["services"]["agent_creator"] = agent_health
    except Exception as e:
        health_status["services"]["agent_creator"] = {
            "status": "error",
            "error": str(e),
        }

    try:
        # Train Model health
        train_health = await train_model.health_check()
        health_status["services"]["train_model"] = train_health
    except Exception as e:
        health_status["services"]["train_model"] = {
            "status": "error",
            "error": str(e),
        }

    try:
        # Pipeline health
        pipeline_health = await pipeline.health_check()
        health_status["services"]["pipeline"] = pipeline_health
    except Exception as e:
        health_status["services"]["pipeline"] = {"status": "error", "error": str(e)}

    try:
        # RAG health
        rag_health = await rag.health_check()
        health_status["services"]["rag"] = rag_health
    except Exception as e:
        health_status["services"]["rag"] = {"status": "error", "error": str(e)}

    # Overall status
    all_healthy = all(
        service.get("status") == "healthy"
        for service in health_status["services"].values()
    )

    health_status["status"] = "healthy" if all_healthy else "degraded"

    return health_status


# System information endpoint
@app.get("/system")
async def system_info():
    """Get system information and statistics."""
    return {
        "system": {
            "platform": "LinkOps Secure AI Platform",
            "version": "1.0.0",
            "environment": "demo",
            "timestamp": datetime.now().isoformat(),
        },
        "services": {
            "model_creator": {
                "port": 8002,
                "status": "running",
                "endpoints": ["/generate-model", "/preview", "/download"],
            },
            "agent_creator": {
                "port": 8003,
                "status": "running",
                "endpoints": ["/generate-agent", "/templates", "/download"],
            },
            "pipeline": {
                "port": 8004,
                "status": "running",
                "endpoints": ["/run-pipeline", "/status", "/download"],
            },
            "rag": {
                "port": 8005,
                "status": "running",
                "endpoints": ["/query", "/embed", "/documents", "/stats"],
            },
            "train_model": {
                "port": 9000,
                "status": "running",
                "endpoints": [
                    "/train-model",
                    "/train-model/status",
                    "/train-model/{model_name}",
                ],
            },
        },
        "security": {
            "cors_enabled": True,
            "trusted_hosts": True,
            "request_logging": True,
            "audit_trail": True,
        },
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors with helpful information."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "path": request.url.path,
            "available_endpoints": {
                "model_creator": "/model-creator/*",
                "agent_creator": "/agent-creator/*",
                "pipeline": "/pipeline/*",
                "rag": "/rag/*",
                "train_model": "/train-model/*",
                "docs": "/docs",
                "health": "/health",
            },
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors with logging."""
    logger.error(f"Internal server error: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": request.url.path,
            "timestamp": datetime.now().isoformat(),
        },
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 Starting LinkOps Unified API...")
    logger.info("📡 Services available:")
    logger.info("   - Model Creator: /model-creator")
    logger.info("   - Agent Creator: /agent-creator")
    logger.info("   - Pipeline: /pipeline")
    logger.info("   - RAG: /rag")
    logger.info("   - Train Model: /train-model")
    logger.info("📚 Documentation: /docs")
    logger.info("💚 Health Check: /health")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down LinkOps Unified API...")


if __name__ == "__main__":
    import uvicorn

    logger.info("🔧 Starting Unified API Server...")
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info", access_log=True)
