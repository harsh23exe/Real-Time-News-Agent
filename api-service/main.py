from dotenv import load_dotenv
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.request_logging import RequestLoggingMiddleware
from utils.logger import logger

# Always load .env from the project root
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Real-Time News Agent API", version="1.0")

# Add request logging middleware (should be first to catch all requests)
app.add_middleware(RequestLoggingMiddleware)

# CORS setup for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🎉 Real-Time News Agent API started successfully!")
    logger.info("📊 Request logging middleware is active")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Real-Time News Agent API is shutting down...")

# Import and include routers (to be created)
from routes.news import news_router
from routes.chat import chat_router

app.include_router(news_router, prefix="/api/v1/news", tags=["news"])
app.include_router(chat_router, prefix="/ws", tags=["chat"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Real-Time News Agent API",
        "version": "1.0"
    } 