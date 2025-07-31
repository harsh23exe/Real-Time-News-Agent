# Real-Time News Agent - Backend Service

A  *backend* service that powers an intelligent news agent capable of real-time news monitoring, semantic search, and AI-powered conversations. This backend provides REST APIs for seamless integration with frontend applications.

Visit: https://techpulse-nu.vercel.app/

## Features

- **Real-time News Ingestion**: Automated pipeline that continuously fetches and indexes news articles
- **Semantic Search**: Vector-based search using Pinecone for intelligent article retrieval
- **AI-Powered Chat**: Integration with Google Gemini for contextual conversations about news
- **Caching System**: Smart caching for headlines to reduce API calls and improve performance
- **Scalable Architecture**: Microservice design with separate API and ingestion services

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Service    │    │ Ingestion       │
│   Application   │◄──►│   (FastAPI)      │    │ Worker          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌──────────────────┐    ┌──────────────────┐
                       │   Pinecone       │    │   NewsAPI        │
                       │   Vector DB      │◄───│   Service        │
                       └──────────────────┘    └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Google Gemini  │
                       │   AI Service     │
                       └──────────────────┘
```

##  Quick Start

### Prerequisites

- Python 3.8+
- Conda environment (recommended)
- API Keys:
  - NewsAPI key
  - Pinecone API key
  - Google Gemini API key

### Environment Setup

1. **Clone and setup environment:**
```bash
git clone https://github.com/harsh23exe/Real-Time-News-Agent.git
cd Real-Time-News-Agent
conda create -n news python=3.8
conda activate news
```

2. **Install dependencies:**
```bash
# Both API Service && Ingestion Service
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
# Create .env files in both api-service/ and ingestion-worker/
NEWS_API_KEY=your_news_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST=your_pinecone_host
PINECONE_INDEX_NAME=your_index_name
GOOGLE_API_KEY=your_gemini_api_key
```

### Running the Services

1. **Start the API Service:**
```bash
cd api-service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Run the Ingestion Pipeline:**
```bash
cd ingestion-worker
python run_pipeline.py --mode headlines --country us --category technology
```

## API Endpoints

### News Search
```http
POST /api/v1/news/search
Content-Type: application/json

{
  "query": "artificial intelligence",
  "limit": 10
}
```

### Top Headlines
```http
GET /api/v1/news/headlines?country=us&category=technology&limit=10
```

### AI Chat
```http
POST /api/v1/chat
Content-Type: application/json

{
  "content": "What are the latest developments in AI?",
  "chat_history": [],
  "selected_news_article": "optional article context"
}
```

### Health Check
```http
GET /health
```

## Ingestion Pipeline

The ingestion worker continuously fetches news articles and indexes them in Pinecone for semantic search:

### Pipeline Modes

- **Headlines Mode**: Fetch top headlines by country/category
- **Topic Mode**: Search articles by specific topics
- **Domain Mode**: Fetch from specific news domains
- **Batch Mode**: Process multiple topics efficiently

### Example Usage

```bash
# Fetch technology headlines
python run_pipeline.py --mode headlines --country us --category technology

# Search for AI-related articles
python run_pipeline.py --mode topic --topics "artificial intelligence"

# Batch process multiple topics
python run_pipeline.py --mode batch --topics "climate change" "renewable energy"
```

## Deployment

```bash
# API Service
cd api-service
uvicorn main:app --reload

# Ingestion Worker (scheduled)
cd ingestion-worker
python run_pipeline.py --mode headlines
```

### Automated Daily Data Ingestion

Set up crontab to automatically feed data daily using the provided script:

```bash
# Make the script executable
chmod +x ingestion-worker/script.sh

# Edit crontab to run daily at 6 AM
crontab -e

# Add this line to run daily at 6:00 AM
0 6 * * * /path/to/Real-Time-News-Agent/ingestion-worker/script.sh >> /path/to/logs/cron.log 2>&1
```

## License

This project is part of the Real-Time News Agent system. See project documentation for licensing details.
