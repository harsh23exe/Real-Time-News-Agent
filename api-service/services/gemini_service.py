import os
import google.genai as genai
from typing import List

class GeminiService:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model or 'gemini-2.5-flash-lite-preview-06-17'
        
        # Configure the Google Generative AI client
        # genai.configure(api_key=self.api_key)
        self.client = genai.Client(api_key=self.api_key)

    def count_tokens(self, text: str) -> int:
        # TODO: Implement accurate token counting for Gemini (placeholder: 1 token per 4 chars)
        return len(text) // 4

    def build_prompt(self, chat_history: List[str], selected_article: str, similar_articles: List[str], user_message: str = None, token_limit: int = 1000000) -> str:
        # Assemble prompt, trimming similar_articles if needed
        prompt = ""
        if chat_history:
            prompt += "Chat history:\n" + "\n".join(chat_history) + "\n"
        if selected_article:
            prompt += "Selected article:\n" + selected_article + "\n"
        if similar_articles:
            prompt += "Similar articles:\n" + "\n".join(similar_articles) + "\n"
        if user_message:
            prompt += "User message:\n" + user_message + "\n"
        # Trim if over token limit
        while self.count_tokens(prompt) > token_limit and similar_articles:
            similar_articles.pop()
            prompt = ""
            if chat_history:
                prompt += "Chat history:\n" + "\n".join(chat_history) + "\n"
            if selected_article:
                prompt += "Selected article:\n" + selected_article + "\n"
            if similar_articles:
                prompt += "Similar articles:\n" + "\n".join(similar_articles) + "\n"
            if user_message:
                prompt += "User message:\n" + user_message + "\n"
        return prompt

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}") 