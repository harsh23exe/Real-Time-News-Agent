import logging
import sys
from datetime import datetime

class Logger:
    """Custom logger class for the ingestion worker"""
    
    def __init__(self, name: str = "ingestion_worker", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        try:
            file_handler = logging.FileHandler(f'logs/ingestion_worker_{datetime.now().strftime("%Y%m%d")}.log')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
        except FileNotFoundError:
            # Create logs directory if it doesn't exist
            import os
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(f'logs/ingestion_worker_{datetime.now().strftime("%Y%m%d")}.log')
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def log_processing_stats(self, stats: dict):
        """Log processing statistics"""
        self.info(f"Processing Statistics: {stats}")
    
    def log_service_status(self, service_name: str, status: dict):
        """Log service status"""
        self.info(f"{service_name} Status: {status}")
    
    def log_error_with_context(self, error: Exception, context: str = ""):
        """Log error with context"""
        error_msg = f"Error in {context}: {str(error)}" if context else str(error)
        self.error(error_msg)

# Global logger instance
logger = Logger() 