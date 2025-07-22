from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Real-Time News Agent API", version="1.0")

# CORS setup for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers (to be created)
from routes.news import news_router
from routes.chat import chat_router

app.include_router(news_router, prefix="/api/v1/news", tags=["news"])
app.include_router(chat_router, prefix="/ws", tags=["chat"]) 