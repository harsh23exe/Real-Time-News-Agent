from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from schemas.chat import UserMessage, BotResponse, ErrorMessage
from services.pinecone_service import PineconeService
from services.gemini_service import GeminiService
import json

chat_router = APIRouter()

@chat_router.websocket("/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Try to receive as JSON first, fallback to text
            try:
                data = await websocket.receive_json()
            except json.JSONDecodeError:
                # If JSON parsing fails, try to receive as text
                text_message = await websocket.receive_text()
                # Create a simple user message from text
                data = {
                    "type": "user_message",
                    "content": text_message,
                    "chat_history": [],
                    "selected_news_article": None
                }
            
            try:
                user_message = UserMessage(**data)
            except Exception as e:
                await websocket.send_json({"type": "error", "message": f"Invalid message format: {str(e)}"})
                continue
                
            chat_history = user_message.chat_history or []
            selected_article = user_message.selected_news_article
            similar_articles = []
            if selected_article:
                # 1. Use Pinecone to find 10 similar articles to selected_article
                pinecone = PineconeService()
                pinecone_result = pinecone.search_similar(query_text=selected_article, top_k=10)
                for match in pinecone_result.get('matches', []):
                    meta = match.get('metadata', {})
                    # Use the 'text' field if available, else join title/summary
                    article_text = meta.get('text') or f"{meta.get('title', '')}\n{meta.get('summary', '')}"
                    similar_articles.append(article_text)
            # 2. Assemble prompt for Gemini
            gemini = GeminiService()
            prompt = gemini.build_prompt(chat_history, selected_article, similar_articles, user_message.content)
            # 3. Call Gemini API
            try:
                gemini_response = gemini.generate_response(prompt)
            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})
                continue
            await websocket.send_json({"type": "bot_response", "content": gemini_response})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)}) 