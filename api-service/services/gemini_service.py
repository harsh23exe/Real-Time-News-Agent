import os
import requests
from typing import List

class GeminiService:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model or 'gemini-2.5-flash-lite-preview-06-17'
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def count_tokens(self, text: str) -> int:
        # TODO: Implement accurate token counting for Gemini (placeholder: 1 token per 4 chars)
        return len(text) // 4

    def build_prompt(self, chat_history: List[str], selected_article: str, similar_articles: List[str], token_limit: int = 1000000) -> str:
        # Assemble prompt, trimming similar_articles if needed
        prompt = ""
        if chat_history:
            prompt += "Chat history:\n" + "\n".join(chat_history) + "\n"
        prompt += "Selected article:\n" + selected_article + "\n"
        if similar_articles:
            prompt += "Similar articles:\n" + "\n".join(similar_articles) + "\n"
        # Trim if over token limit
        while self.count_tokens(prompt) > token_limit and similar_articles:
            similar_articles.pop()
            prompt = ""
            if chat_history:
                prompt += "Chat history:\n" + "\n".join(chat_history) + "\n"
            prompt += "Selected article:\n" + selected_article + "\n"
            if similar_articles:
                prompt += "Similar articles:\n" + "\n".join(similar_articles) + "\n"
        return prompt

    def generate_response(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        }
        response = requests.post(self.api_url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            result = response.json()
            # Parse Gemini response (adjust as needed for actual API response structure)
            return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        else:
            raise Exception(f"Gemini API error: {response.status_code} {response.text}") 