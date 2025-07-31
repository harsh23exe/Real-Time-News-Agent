from fastapi import APIRouter, HTTPException
from schemas.chat import UserMessage, BotResponse, ErrorMessage
from services.pinecone_service import PineconeService
from services.gemini_service import GeminiService

chat_router = APIRouter()

@chat_router.post("/chat")
async def chat_endpoint(user_message: UserMessage):
    try:
        chat_history = user_message.chat_history or []
        selected_article = user_message.selected_news_article
        similar_articles = []
        
        if selected_article:
            # 1. Use Pinecone to find 10 similar articles to selected_article
            pinecone = PineconeService()
            pinecone_result = pinecone.search_similar(query_text=selected_article, top_k=20)
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
            raise HTTPException(status_code=500, detail=str(e))
        
        return BotResponse(content=gemini_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 