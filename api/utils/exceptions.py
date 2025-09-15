"""
Custom exceptions for the application
"""

from fastapi import HTTPException
from typing import Optional, Any, Dict


class ConverterBaseException(Exception):
    """Base exception for converter-related errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class FileProcessingError(ConverterBaseException):
    """Raised when file processing fails"""
    pass


class UnsupportedFileFormatError(ConverterBaseException):
    """Raised when file format is not supported"""
    pass


class AIProcessingError(ConverterBaseException):
    """Raised when AI processing fails"""
    pass


class ValidationError(ConverterBaseException):
    """Raised when validation fails"""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized HTTP exception
    
    Args:
        status_code: HTTP status code
        message: Error message
        error_code: Optional error code
        details: Optional additional details
    
    Returns:
        HTTPException with structured error response
    """
    
    detail = {
        "error": message,
        "status": "ERROR",
        "timestamp": "2025-09-05T11:00:00Z"
    }
    
    if error_code:
        detail["error_code"] = error_code
    
    if details:
        detail["details"] = details
    
    return HTTPException(status_code=status_code, detail=detail)
