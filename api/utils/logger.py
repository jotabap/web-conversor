"""
Custom logger configuration for Azure Functions
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'ENDC': '\033[0m'       # End color
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['ENDC'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['ENDC']}"
        return super().format(record)


def setup_logger(
    name: str = __name__,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a colored logger with custom formatting
    
    Args:
        name: Logger name
        level: Logging level
        format_string: Custom format string
    
    Returns:
        Configured logger instance
    """
    
    if format_string is None:
        format_string = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = ColoredFormatter(format_string)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def setup_azure_logger(level: str = "INFO") -> logging.Logger:
    """
    Set up logger specifically for Azure Functions
    
    Args:
        level: Logging level
    
    Returns:
        Configured Azure Functions logger
    """
    # Azure Functions uses the root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Azure Functions automatically handles logging output
    # No need to add handlers as Azure handles this
    
    return logger


# Create default logger instance
logger = setup_logger("matrix_ai_converter")
