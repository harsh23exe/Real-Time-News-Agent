import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).resolve().parents[1] / 'logs'
logs_dir.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger('api-service')
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if logger is imported multiple times
if not logger.hasHandlers():
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation (10MB max, keep 5 backup files)
    log_filename = logs_dir / 'api-service.log'
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Set formatters
    console_handler.setFormatter(simple_formatter)
    file_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info("Logger initialized with console and file handlers") 