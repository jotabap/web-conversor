"""
Pydantic models for API requests
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class FileFormat(str, Enum):
    """Supported file formats"""
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"


class ConversionRequest(BaseModel):
    """Request model for file conversion"""
    
    use_ai: bool = Field(
        default=True,
        description="Whether to use AI-powered analysis"
    )
    
    min_confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for AI analysis"
    )
    
    sheet_name: Optional[str] = Field(
        default=None,
        description="Specific sheet name for Excel files"
    )
    
    skip_rows: int = Field(
        default=0,
        ge=0,
        description="Number of rows to skip from the beginning"
    )
    
    max_rows: Optional[int] = Field(
        default=None,
        gt=0,
        description="Maximum number of rows to process"
    )


class JsonToExcelRequest(BaseModel):
    """Request model for JSON to Excel conversion"""
    
    json_data: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(
        ..., 
        description="JSON data to convert to Excel"
    )
    
    use_ai: bool = Field(
        default=False,  # Por defecto False para conversiones simples
        description="Whether to use AI-powered optimization"
    )
    
    sheet_name: str = Field(
        default="Sheet1",
        description="Name of the Excel sheet"
    )
    
    min_confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for AI analysis"
    )
    
    apply_formatting: bool = Field(
        default=True,
        description="Whether to apply basic Excel formatting"
    )
    
    optimize_layout: bool = Field(
        default=False,
        description="Whether to optimize the Excel layout (requires AI)"
    )
    
    @field_validator('optimize_layout')
    @classmethod
    def validate_optimize_layout(cls, v, info):
        """If optimize_layout is True, use_ai should also be True"""
        if v and not info.data.get('use_ai', False):
            raise ValueError('optimize_layout requires use_ai to be True')
        return v


class FileUploadRequest(BaseModel):
    """Request model for file upload metadata"""
    
    filename: str = Field(..., description="Name of the uploaded file")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate file extension"""
        if not any(v.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
            raise ValueError('Unsupported file format')
        return v
    
    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        """Validate file size (max 10MB)"""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size exceeds maximum limit of {max_size} bytes')
        return v


class SqlGenerationRequest(BaseModel):
    """Request model for SQL generation from Excel/JSON data"""
    
    table_name: str = Field(
        default="data_table",
        description="Target SQL table name"
    )
    
    sql_type: str = Field(
        default="insert",
        description="Type of SQL to generate (insert or update)",
        pattern="^(insert|update)$"
    )
    
    use_ai: bool = Field(
        default=True,
        description="Whether to use AI for SQL optimization"
    )
    
    batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Number of records per INSERT batch"
    )
    
    key_columns: Optional[List[str]] = Field(
        default=None,
        description="Key columns for UPDATE statements (auto-detected if not provided)"
    )
    
    include_create_table: bool = Field(
        default=True,
        description="Include CREATE TABLE statement in output"
    )
    
    optimize_performance: bool = Field(
        default=True,
        description="Apply performance optimizations to generated SQL"
    )
