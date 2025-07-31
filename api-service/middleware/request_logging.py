import time
import json
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from utils.logger import logger
from typing import Optional, Dict, Any


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Extract request information
        client_host = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params) if request.query_params else {}
        
        # Log incoming request
        logger.info(f" {method} {path} - Client: {client_host}")
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Extract response information
            status_code = response.status_code
            
            # Choose log level based on status code
            if status_code >= 500:
                logger.error(f"{method} {path} - {status_code} - {process_time*1000:.2f}ms - Client: {client_host}")
            elif status_code >= 400:
                logger.warning(f"{method} {path} - {status_code} - {process_time*1000:.2f}ms - Client: {client_host}")
            else:
                logger.info(f" {method} {path} - {status_code} - {process_time*1000:.2f}ms - Client: {client_host}")
            
            # Add custom headers to response
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Calculate processing time even for errors
            process_time = time.time() - start_time
            
            # Log error
            logger.error(f" {method} {path} - ERROR: {str(e)} - {process_time*1000:.2f}ms - Client: {client_host}")
            
            # Re-raise the exception
            raise e
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (common in load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if request.client:
            return request.client.host
        
        return "Unknown" 