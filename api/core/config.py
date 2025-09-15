"""
Application configuration settings for Azure Functions
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings for Azure Functions"""
    
    # App Info
    app_name: str = "Matrix AI Converter"
    app_version: str = "2.1.0"
    app_description: str = "Neural Network-powered Excel to JSON conversion service"
    
    # File Processing
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".xlsx", ".xls", ".csv"]
    
    # AI Settings
    default_confidence_threshold: float = 0.8
    ai_enabled: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_model: str = "gpt-4"
    
    # AI Processing Settings
    ai_max_tokens: int = 4000
    ai_temperature: float = 0.3
    ai_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class AzureSettings(BaseSettings):
    """Azure Functions specific settings using Azure App Settings"""
    
    # App Info
    app_name: str = "Matrix AI Converter"
    app_version: str = "2.1.0"
    app_description: str = "Neural Network-powered Excel to JSON conversion service"
    
    # File Processing - Read from Azure App Settings
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    allowed_extensions: List[str] = [".xlsx", ".xls", ".csv"]
    
    # AI Settings
    default_confidence_threshold: float = float(os.getenv("DEFAULT_CONFIDENCE_THRESHOLD", "0.8"))
    ai_enabled: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Azure OpenAI Configuration - Read from Azure App Settings
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    azure_openai_model: str = os.getenv("AZURE_OPENAI_MODEL", "gpt-4")
    
    # AI Processing Settings
    ai_max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "4000"))
    ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0.3"))
    ai_timeout: int = int(os.getenv("AI_TIMEOUT", "30"))


# Global settings instances
settings = Settings()


def get_azure_settings() -> AzureSettings:
    """Get Azure Functions settings from environment variables"""
    return AzureSettings()
