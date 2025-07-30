import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logger
logger = logging.getLogger('api-service')
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if logger is imported multiple times
if not logger.hasHandlers():
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Set formatter for console handler
    console_handler.setFormatter(simple_formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Try to add file handler only if we're not in a serverless environment
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).resolve().parents[1] / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # File handler with rotation (10MB max, keep 5 backup files)
        log_filename = logs_dir / 'api-service.log'
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
        
        logger.info("Logger initialized with console and file handlers")
        
    except (OSError, PermissionError):
        # We're in a serverless environment (read-only file system)
        # Only use console logging
        logger.info("Logger initialized with console handler only (serverless environment detected)") 