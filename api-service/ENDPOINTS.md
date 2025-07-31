# API Endpoints Documentation

This document provides comprehensive documentation for all available API endpoints in the Real-Time News Agent backend service.



## REST API Endpoints

### 1. Health Check
**GET** `/health`

Check the health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "service": "Real-Time News Agent API",
  "version": "1.0"
}
```

**Status Codes:**
- `200`: Service is healthy

---

### 2. Search News Articles
**POST** `/api/v1/news/search`

Search for news articles using semantic search via Pinecone vector database.

**Request Body:**
```json
{
  "query": "artificial intelligence developments",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "ai_2024-01-01T12:00:00_12345",
      "title": "Latest AI Breakthrough in Machine Learning",
      "url": "https://example.com/ai-article",
      "summary": "Researchers have made significant progress in...",
      "published_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Status Codes:**
- `200`: Search completed successfully
- `400`: Invalid request parameters
- `500`: Internal server error

**Frontend Integration:**
- Search bar with real-time suggestions
- Paginated results display
- Clickable article cards with metadata

---

### 3. Get Top Headlines
**GET** `/api/v1/news/headlines`

Retrieve top headlines with caching support for improved performance.

**Query Parameters:**
- `country` (string, optional): Country code (default: "us")
- `category` (string, optional): News category (default: "technology")
- `limit` (integer, optional): Number of headlines to return (default: 10)

**Example Request:**
```
GET /api/v1/news/headlines?country=us&category=technology&limit=5
```

**Response:**
```json
{
  "results": [
    {
      "id": "headlines_2024-01-01T12:00:00_67890",
      "title": "Tech Giant Announces New AI Platform",
      "url": "https://example.com/tech-news",
      "summary": "Major technology company launches innovative AI solution...",
      "published_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Status Codes:**
- `200`: Headlines retrieved successfully
- `500`: Internal server error

**Features:**
- Smart caching system for improved performance
- Automatic storage in Pinecone for semantic search
- Support for multiple countries and categories

---

### 4. Fetch Records by ID
**POST** `/api/v1/news/fetch`

Retrieve specific news articles by their Pinecone record IDs.

**Request Body:**
```json
{
  "ids": ["record_id_1", "record_id_2", "record_id_3"]
}
```

**Response:**
```json
{
  "success": true,
  "records": {
    "record_id_1": {
      "id": "record_id_1",
      "metadata": {
        "title": "Article Title",
        "url": "https://example.com/article",
        "summary": "Article summary...",
        "published_at": "2024-01-01T12:00:00"
      }
    }
  },
  "namespace": "news",
  "usage": {
    "read_units": 3
  },
  "total_fetched": 1
}
```

**Status Codes:**
- `200`: Records fetched successfully
- `400`: Invalid request parameters
- `500`: Internal server error

---

### 5. AI Chat Endpoint
**POST** `/api/v1/chat`

Engage in AI-powered conversations about news topics using Google Gemini.

**Request Body:**
```json
{
  "type": "user_message",
  "content": "What are the latest developments in renewable energy?",
  "chat_history": [
    "User: Tell me about climate change",
    "Bot: Climate change is a significant global challenge..."
  ],
  "selected_news_article": "optional article context for more specific responses"
}
```

**Response:**
```json
{
  "type": "bot_response",
  "content": "Based on recent news articles, there have been several significant developments in renewable energy..."
}
```

**Status Codes:**
- `200`: Chat response generated successfully
- `400`: Invalid request parameters
- `500`: AI service error or internal server error

**Features:**
- Context-aware responses using chat history
- Integration with news articles for factual responses
- Semantic search for relevant articles
- Google Gemini AI integration


## Rate Limiting

Rate Limit will soon be provided.
