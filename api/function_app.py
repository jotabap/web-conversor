"""
Azure Functions - Matrix AI Converter
Neural Network-powered Excel to JSON conversion service
"""

import azure.functions as func
import logging
import json
import os
from typing import Optional

# Import our existing modules (we'll adapt these)
from core.config import get_azure_settings
from utils.logger import setup_azure_logger
from services.converter_service import ConverterService
from models.responses import (
    HealthResponse, 
    RootResponse, 
    ConversionResponse, 
    ErrorResponse
)

# Initialize the Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Setup logging for Azure Functions
logger = setup_azure_logger()

# Initialize services
converter_service = ConverterService()

# CORS headers helper
def get_cors_headers():
    """Get CORS headers for all responses"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }


# OPTIONS handler for CORS preflight
@app.route(route="{*route}", methods=["OPTIONS"])
def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    """Handle CORS preflight requests"""
    return func.HttpResponse(
        "",
        status_code=200,
        headers=get_cors_headers()
    )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for Azure Functions
    """
    try:
        logger.info("Health check performed")
        
        response = HealthResponse(
            status="ONLINE",
            neural_network="ACTIVE",
            ai_engine="READY"
        )
        
        return func.HttpResponse(
            response.model_dump_json(),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        error_response = ErrorResponse(
            error="Health check failed",
            error_code="HEALTH_CHECK_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="", methods=["GET"])
def root(req: func.HttpRequest) -> func.HttpResponse:
    """
    Root endpoint with Matrix-style response
    """
    try:
        logger.info("Root endpoint accessed")
        
        settings = get_azure_settings()
        
        response = RootResponse(
            error="🔋MATRIX AI CONVERTER - NEURAL NETWORK ONLINE",
            status="ACTIVE", 
            version=settings.app_version,
            protocols=["EXCEL→JSON", "JSON→EXCEL", "EXCEL→SQL"]
        )
        
        return func.HttpResponse(
            response.model_dump_json(),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"Root endpoint failed: {str(e)}")
        error_response = ErrorResponse(
            error="Service unavailable",
            error_code="SERVICE_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="info", methods=["GET"])
def app_info(req: func.HttpRequest) -> func.HttpResponse:
    """
    Application information endpoint
    """
    try:
        settings = get_azure_settings()
        
        info = {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description,
            "environment": "Azure Functions",
            "ai_enabled": settings.ai_enabled,
            "max_file_size": f"{settings.max_file_size / (1024*1024):.1f}MB",
            "allowed_extensions": settings.allowed_extensions
        }
        
        return func.HttpResponse(
            json.dumps(info),
            status_code=200,
            headers=get_cors_headers()
        )
    except Exception as e:
        logger.error(f"Info endpoint failed: {str(e)}")
        error_response = ErrorResponse(
            error="Info unavailable",
            error_code="INFO_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="convert/excel-to-json", methods=["POST"])
async def convert_excel_to_json(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert Excel or CSV file to JSON format using AI analysis
    Azure Functions version
    """
    try:
        logger.info("📄 Excel to JSON conversion requested")
        
        # Get file from request
        files = req.files
        if not files or 'file' not in files:
            error_response = ErrorResponse(
                error="No file provided",
                error_code="NO_FILE_PROVIDED"
            )
            return func.HttpResponse(
                error_response.model_dump_json(),
                status_code=400,
                headers=get_cors_headers()
            )
        
        file = files['file']
        
        # Get parameters from form data or query params
        use_ai = req.params.get('use_ai', 'true').lower() == 'true'
        min_confidence = float(req.params.get('min_confidence', '0.8'))
        sheet_name = req.params.get('sheet_name')
        skip_rows = int(req.params.get('skip_rows', '0'))
        max_rows = req.params.get('max_rows')
        max_rows = int(max_rows) if max_rows else None
        
        # Process the conversion
        result = await converter_service.convert_excel_to_json(
            file_content=file.read(),
            filename=file.filename,
            use_ai=use_ai,
            min_confidence=min_confidence,
            sheet_name=sheet_name,
            skip_rows=skip_rows,
            max_rows=max_rows
        )
        
        response = ConversionResponse(
            status=result.get('status', 'SUCCESS'),
            data=result.get('data', []),
            metadata=result.get('metadata', {})
        )
        
        return func.HttpResponse(
            response.model_dump_json(),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        error_response = ErrorResponse(
            error=f"Conversion failed: {str(e)}",
            error_code="CONVERSION_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="convert/formats", methods=["GET"])
def get_formats(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get supported file formats
    """
    try:
        logger.info("📋 Formats endpoint accessed")
        
        formats = {
            "supported_input_formats": [".xlsx", ".xls", ".csv"],
            "supported_output_formats": ["json", "excel", "sql"],
            "max_file_size_mb": 10,
            "features": {
                "ai_analysis": True,
                "batch_processing": False,
                "custom_sheets": True
            }
        }
        
        return func.HttpResponse(
            json.dumps(formats),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Formats endpoint failed: {str(e)}")
        error_response = ErrorResponse(
            error="Could not retrieve formats",
            error_code="FORMATS_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="convert/json-to-excel", methods=["POST"])
async def convert_json_to_excel(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert JSON data to Excel format
    """
    try:
        logger.info("INFO: JSON to Excel conversion requested")
        
        # Get JSON data from request body
        try:
            request_body = req.get_json()
            if not request_body or 'data' not in request_body:
                error_response = ErrorResponse(
                    error="No JSON data provided in request body",
                    error_code="NO_DATA_PROVIDED"
                )
                return func.HttpResponse(
                    error_response.model_dump_json(),
                    status_code=400,
                    headers=get_cors_headers()
                )
            
            json_data = request_body['data']
            filename = request_body.get('filename', 'converted_data.xlsx')
            apply_formatting = request_body.get('apply_formatting', True)
            
        except Exception as e:
            error_response = ErrorResponse(
                error="Invalid JSON in request body",
                error_code="INVALID_JSON"
            )
            return func.HttpResponse(
                error_response.model_dump_json(),
                status_code=400,
                headers=get_cors_headers()
            )
        
        # Process the conversion
        result = await converter_service.convert_json_to_excel(
            json_data=json_data,
            filename=filename,
            apply_formatting=apply_formatting
        )
        
        # Return the Excel file as base64
        import base64
        excel_b64 = base64.b64encode(result['excel_content']).decode('utf-8')
        
        response_data = {
            "success": True,
            "message": "JSON converted to Excel successfully",
            "filename": result['filename'],
            "excel_base64": excel_b64,
            "metadata": result.get('metadata', {})
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"JSON to Excel conversion failed: {str(e)}")
        error_response = ErrorResponse(
            message=f"JSON to Excel conversion failed: {str(e)}",
            error_code="JSON_TO_EXCEL_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


@app.route(route="convert/excel-to-sql", methods=["POST"])
async def convert_excel_to_sql(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert Excel file to SQL queries
    """
    try:
        logger.info("INFO: Excel to SQL conversion requested")
        
        # Get file from request
        files = req.files
        if not files or 'file' not in files:
            error_response = ErrorResponse(
                error="No file provided",
                error_code="NO_FILE_PROVIDED"
            )
            return func.HttpResponse(
                error_response.model_dump_json(),
                status_code=400,
                headers=get_cors_headers()
            )
        
        file = files['file']
        
        # Get parameters
        table_name = req.params.get('table_name', 'converted_data')
        include_create_table = req.params.get('include_create_table', 'true').lower() == 'true'
        include_inserts = req.params.get('include_inserts', 'true').lower() == 'true'
        
        # Process the conversion
        result = await converter_service.convert_excel_to_sql(
            file_content=file.read(),
            filename=file.filename,
            table_name=table_name,
            include_create_table=include_create_table,
            include_inserts=include_inserts
        )
        
        response_data = {
            "success": True,
            "message": "Excel converted to SQL successfully",
            "sql_queries": result.get('sql_queries', {}),
            "metadata": result.get('metadata', {})
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers=get_cors_headers()
        )
        
    except Exception as e:
        logger.error(f"Excel to SQL conversion failed: {str(e)}")
        error_response = ErrorResponse(
            message=f"Excel to SQL conversion failed: {str(e)}",
            error_code="EXCEL_TO_SQL_ERROR"
        )
        return func.HttpResponse(
            error_response.model_dump_json(),
            status_code=500,
            headers=get_cors_headers()
        )


if __name__ == "__main__":
    # This won't be used in Azure Functions, but useful for local testing
    import uvicorn
    logger.info("🌟 Starting Azure Functions locally")
