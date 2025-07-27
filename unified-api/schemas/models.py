#!/usr/bin/env python3
"""
ML Model Schemas
===============

Comprehensive schemas for ML model management, training, and prediction.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Supported model types."""

    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    VENDOR_SUGGESTION = "vendor_suggestion"
    MAINTENANCE_PREDICTOR = "maintenance_predictor"
    COST_ESTIMATOR = "cost_estimator"


class ModelStatus(str, Enum):
    """Model training and deployment status."""

    PENDING = "pending"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    RETRAINING = "retraining"


class FeatureType(str, Enum):
    """Feature data types for model training."""

    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    DATE = "date"
    BOOLEAN = "boolean"


class VendorSuggestionFeatures(BaseModel):
    """Enhanced vendor suggestion model features."""

    quality_of_work: float = Field(..., description="Quality score (1-10)")
    response_time: float = Field(..., description="Response time in hours")
    completion_time: float = Field(..., description="Completion time in hours")
    cost: float = Field(..., description="Project cost in dollars")
    repaired: bool = Field(False, description="Whether repairs were needed")
    new_install: bool = Field(False, description="Whether it's a new installation")
    cost_threshold: float = Field(1000.0, description="Cost threshold for approval")
    emergency_work: bool = Field(False, description="Whether it's emergency work")
    warranty_available: bool = Field(True, description="Whether warranty is available")
    insurance_verified: bool = Field(True, description="Whether insurance is verified")


class ModelConfig(BaseModel):
    """Model configuration for training."""

    name: str = Field(..., description="Model name")
    model_type: ModelType = Field(..., description="Type of model to train")
    target_column: str = Field(..., description="Target column for prediction")
    feature_columns: list[str] = Field(..., description="Feature columns for training")
    test_size: float = Field(0.2, description="Test set size (0.0-1.0)")
    random_state: int = Field(42, description="Random seed for reproducibility")
    max_iterations: int = Field(1000, description="Maximum training iterations")
    learning_rate: float = Field(0.01, description="Learning rate")
    include_demo_data: bool = Field(True, description="Include demo data in training")
    auto_sync: bool = Field(False, description="Enable automatic retraining")


class TrainingRequest(BaseModel):
    """Request for model training."""

    model_configuration: ModelConfig
    csv_path: Optional[str] = Field(None, description="Path to training CSV file")
    csv_data: Optional[str] = Field(None, description="CSV data as string")
    quick_training: bool = Field(False, description="Use quick training mode")
    retrain_existing: bool = Field(False, description="Retrain existing model")


class TrainingProgress(BaseModel):
    """Training progress information."""

    model_name: str
    status: ModelStatus
    progress: float = Field(0.0, description="Training progress (0-100)")
    current_step: str = Field("", description="Current training step")
    estimated_time: Optional[float] = Field(
        None, description="Estimated time remaining"
    )
    start_time: datetime
    last_update: datetime


class ModelMetrics(BaseModel):
    """Model performance metrics."""

    mae: float = Field(..., description="Mean Absolute Error")
    mse: float = Field(..., description="Mean Squared Error")
    rmse: float = Field(..., description="Root Mean Squared Error")
    r2: float = Field(..., description="R-squared score")
    accuracy: Optional[float] = Field(None, description="Classification accuracy")
    precision: Optional[float] = Field(None, description="Classification precision")
    recall: Optional[float] = Field(None, description="Classification recall")
    f1_score: Optional[float] = Field(None, description="F1 score")


class VendorRecommendation(BaseModel):
    """Vendor recommendation result."""

    contractor: str = Field(..., description="Contractor name")
    quality_score: float = Field(..., description="Quality score (1-10)")
    cost_score: float = Field(..., description="Cost efficiency score")
    reliability_score: float = Field(..., description="Reliability score")
    overall_score: float = Field(..., description="Overall recommendation score")
    specialties: list[str] = Field([], description="Contractor specialties")
    availability: str = Field("", description="Availability status")
    estimated_cost: float = Field(0.0, description="Estimated project cost")
    estimated_time: float = Field(0.0, description="Estimated completion time")


class TrainingResult(BaseModel):
    """Complete training result."""

    model_name: str
    model_type: ModelType
    status: ModelStatus
    metrics: ModelMetrics
    training_time: float = Field(..., description="Training time in seconds")
    model_path: str = Field(..., description="Path to saved model")
    feature_importance: dict[str, float] = Field(
        {}, description="Feature importance scores"
    )
    vendor_recommendations: list[VendorRecommendation] = Field(
        [], description="Vendor recommendations"
    )
    training_data_size: int = Field(..., description="Number of training samples")
    test_data_size: int = Field(..., description="Number of test samples")
    created_at: datetime
    updated_at: datetime


class PredictionRequest(BaseModel):
    """Request for model prediction."""

    model_name: str = Field(..., description="Name of the model to use")
    features: dict[str, Any] = Field(..., description="Input features for prediction")
    include_confidence: bool = Field(True, description="Include confidence scores")


class PredictionResult(BaseModel):
    """Model prediction result."""

    model_name: str
    prediction: Union[float, int, str] = Field(..., description="Predicted value")
    confidence: Optional[float] = Field(None, description="Prediction confidence")
    feature_contributions: dict[str, float] = Field(
        {}, description="Feature contributions"
    )
    recommendations: list[str] = Field([], description="Additional recommendations")
    processing_time: float = Field(..., description="Prediction processing time")


class ModelInfo(BaseModel):
    """Model information for listing and management."""

    name: str
    model_type: ModelType
    status: ModelStatus
    created_at: datetime
    updated_at: datetime
    training_data_size: int
    metrics: Optional[ModelMetrics] = None
    description: Optional[str] = None
    version: str = Field("1.0.0", description="Model version")
    tags: list[str] = Field([], description="Model tags")


class AutoSyncConfig(BaseModel):
    """Configuration for automatic model retraining."""

    enabled: bool = Field(False, description="Enable auto-sync")
    schedule: str = Field("daily", description="Sync schedule (daily, weekly, monthly)")
    trigger_conditions: list[str] = Field(
        [], description="Conditions that trigger retraining"
    )
    demo_data_included: bool = Field(True, description="Include demo data in auto-sync")
    max_models: int = Field(10, description="Maximum number of models to maintain")
    retention_days: int = Field(30, description="Days to retain old models")


class ModelDeployment(BaseModel):
    """Model deployment configuration."""

    model_name: str
    environment: str = Field("production", description="Deployment environment")
    endpoint_url: Optional[str] = Field(None, description="API endpoint URL")
    health_check_url: Optional[str] = Field(None, description="Health check endpoint")
    deployment_time: datetime
    status: str = Field("active", description="Deployment status")
    replicas: int = Field(1, description="Number of model replicas")
    resources: dict[str, Any] = Field({}, description="Resource requirements")


# Response models for API endpoints
class TrainingResponse(BaseModel):
    """Response for training requests."""

    success: bool
    model_name: str
    result: Optional[TrainingResult] = None
    error: Optional[str] = None
    message: str


class PredictionResponse(BaseModel):
    """Response for prediction requests."""

    success: bool
    result: Optional[PredictionResult] = None
    error: Optional[str] = None
    message: str


class ModelListResponse(BaseModel):
    """Response for model listing."""

    models: list[ModelInfo]
    total_count: int
    page: int
    page_size: int


class HealthCheckResponse(BaseModel):
    """Response for health check."""

    status: str
    timestamp: datetime
    model_count: int
    active_deployments: int
    system_health: str
