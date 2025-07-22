from pydantic import BaseModel
from typing import List, Optional

class UserMessage(BaseModel):
    type: str = "user_message"
    content: str
    chat_history: Optional[List[str]] = None
    selected_news_article: str

class BotResponse(BaseModel):
    type: str = "bot_response"
    content: str

class ErrorMessage(BaseModel):
    type: str = "error"
    message: str 