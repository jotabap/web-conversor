"""
Pydantic models for API responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class AIUsageInfo(BaseModel):
    """Information about AI usage during processing"""
    
    ai_used: bool = Field(..., description="Whether AI was used")
    processing_mode: str = Field(..., description="Processing mode used (deterministic, ai_assisted, fallback)")
    trigger_reason: Optional[str] = Field(default=None, description="Why AI was triggered")
    issues_detected: List[str] = Field(default_factory=list, description="Specific issues that triggered AI")
    ai_improvements: List[str] = Field(default_factory=list, description="AI improvements applied")
    user_friendly_explanation: str = Field(..., description="Simple explanation for the user")
    technical_details: Optional[Dict[str, Any]] = Field(default=None, description="Technical details for developers")


class AIAnalysis(BaseModel):
    """AI analysis result model"""
    
    confidence: float = Field(..., ge=0.0, le=100.0, description="Analysis confidence percentage")
    analysis_type: str = Field(..., description="Type of analysis performed")
    detected_patterns: List[str] = Field(default_factory=list, description="Detected data patterns")
    column_types: Dict[str, str] = Field(default_factory=dict, description="Detected column types")
    recommendations: List[str] = Field(default_factory=list, description="AI recommendations")


class ConversionMetadata(BaseModel):
    """Metadata for conversion results"""
    
    record_count: int = Field(..., ge=0, description="Number of records processed")
    columns: List[str] = Field(..., description="Column names")
    ai_analysis: AIAnalysis = Field(..., description="AI analysis results")
    ai_usage: AIUsageInfo = Field(..., description="AI usage information")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Overall confidence")
    processing_time: str = Field(..., description="Processing time")
    file_info: Optional[Dict[str, Any]] = Field(default=None, description="Original file information")


class ConversionResponse(BaseModel):
    """Response model for successful conversion"""
    
    status: str = Field(default="SUCCESS", description="Operation status")
    data: List[Dict[str, Any]] = Field(..., description="Converted data")
    metadata: ConversionMetadata = Field(..., description="Conversion metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response model"""
    
    status: str = Field(default="ONLINE", description="Service status")
    neural_network: str = Field(default="ACTIVE", description="Neural network status")
    ai_engine: str = Field(default="READY", description="AI engine status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class RootResponse(BaseModel):
    """Root endpoint response model"""
    
    message: str = Field(default="🔋 MATRIX AI CONVERTER - NEURAL NETWORK ONLINE")
    status: str = Field(default="ACTIVE")
    version: str = Field(default="2.1.0")
    protocols: List[str] = Field(default=["EXCEL→JSON", "JSON→EXCEL", "EXCEL→SQL"])


class JsonToExcelResponse(BaseModel):
    """Response model for JSON to Excel conversion"""
    
    status: str = Field(default="SUCCESS", description="Operation status")
    filename: str = Field(..., description="Generated Excel filename")
    download_url: str = Field(..., description="URL to download the file")
    metadata: Dict[str, Any] = Field(..., description="Conversion metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class SqlGenerationResponse(BaseModel):
    """Response model for SQL generation"""
    
    status: str = Field(default="SUCCESS", description="Operation status")
    sql_type: str = Field(..., description="Type of SQL generated (insert/update)")
    statements: Dict[str, Any] = Field(..., description="Generated SQL statements")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")
    download_url: Optional[str] = Field(default=None, description="URL to download SQL file")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: str = Field(..., description="Error message")
    status: str = Field(default="ERROR", description="Error status")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
