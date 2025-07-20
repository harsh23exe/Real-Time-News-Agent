# News Ingestion Pipeline

This pipeline fetches news articles from NewsAPI and uploads them to a Pinecone vector database for real-time news processing and retrieval.

## Overview

The `NewsPipeline` class orchestrates the entire process of:
1. Fetching news articles from NewsAPI
2. Processing and preparing article text for vectorization
3. Uploading articles to Pinecone vector database with metadata
4. Providing comprehensive logging and error handling

## Features

- **Multiple Ingestion Modes**: Topic-based, headlines, domain-specific, and batch processing
- **Comprehensive Metadata**: Stores article metadata including title, description, URL, source, author, and timestamps
- **Error Handling**: Robust error handling with detailed logging
- **Batch Processing**: Process multiple topics efficiently
- **Status Monitoring**: Check pipeline and service status

## NewsAPI Date Constraint

> **Note:** NewsAPI only allows retrieving news from previous days (not the current day). The pipeline does not support a `from_date` parameter and always fetches the most recent available news.

## Configuration

Before running the pipeline, ensure you have the following environment variables set:

```bash
# Required API Keys
NEWS_API_KEY=your_news_api_key
PINECONE_API_KEY=your_pinecone_api_key

# Pinecone Configuration
PINECONE_HOST=your_pinecone_host
PINECONE_INDEX_NAME=your_index_name
PINECONE_NAMESPACE=your_namespace
```

## Usage

### Command Line Interface

The pipeline can be run using the `run_pipeline.py` script:

```bash
# Process a single topic
python run_pipeline.py --mode topic --topics "artificial intelligence"

# Process top headlines
python run_pipeline.py --mode headlines --country us --category technology

# Process news from a specific domain
python run_pipeline.py --mode domain --domain "techcrunch.com"

# Process multiple topics in batch
python run_pipeline.py --mode batch --topics "climate change" "renewable energy" "electric vehicles"
```

### Programmatic Usage

```python
from services.news_pipeline import NewsPipeline

# Initialize pipeline
pipeline = NewsPipeline()

# Process a single topic
result = pipeline.process_news_topic(
    topic="artificial intelligence",
    language="en",
    sort_by="publishedAt"
)

# Process top headlines
result = pipeline.process_top_headlines(
    country="us",
    category="technology"
)

# Process domain-specific news
result = pipeline.process_domain_news(
    domain="techcrunch.com"
)

# Batch process multiple topics
topics = ["climate change", "renewable energy", "electric vehicles"]
result = pipeline.batch_process_topics(
    topics=topics
)

# Check pipeline status
status = pipeline.get_pipeline_status()

# Clean up
pipeline.close()
```

## Pipeline Modes

### 1. Topic Mode
Fetches news articles based on specific topics or keywords.

```python
result = pipeline.process_news_topic(
    topic="artificial intelligence",
    language="en",
    sort_by="publishedAt"
)
```

### 2. Headlines Mode
Fetches top headlines from specific countries and categories.

```python
result = pipeline.process_top_headlines(
    country="us",
    category="technology"  # Optional
)
```

### 3. Domain Mode
Fetches news from specific domains or news sources.

```python
result = pipeline.process_domain_news(
    domain="techcrunch.com"
)
```

### 4. Batch Mode
Process multiple topics efficiently in a single pipeline run.

```python
topics = ["AI", "machine learning", "deep learning"]
result = pipeline.batch_process_topics(
    topics=topics
)
```

## Response Format

All pipeline methods return a standardized response format:

```python
{
    'success': True,
    'topic': 'artificial intelligence',  # or other relevant fields
    'articles_fetched': 10,
    'articles_processed': 9,
    'articles_failed': 1,
    'timestamp': '2024-01-01T12:00:00'
}
```

## Error Handling

The pipeline includes comprehensive error handling:

- **Configuration Validation**: Ensures all required API keys are present
- **Service Failures**: Handles NewsAPI and Pinecone service failures gracefully
- **Individual Article Failures**: Continues processing even if individual articles fail
- **Detailed Logging**: Provides detailed logs for debugging

## Testing

Run the pipeline tests:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_news_pipeline

# Run with conda environment
conda activate news
python -m unittest tests.test_news_pipeline
```

## Example Output

```
=== Pipeline Results ===
Success: True
Articles fetched: 15
Articles processed: 14
Articles failed: 1
Timestamp: 2024-01-01T12:00:00
```

## Dependencies

The pipeline requires the following services to be properly configured:

1. **NewsAPI Service**: Handles fetching news articles
2. **Pinecone Service**: Handles vector database operations
3. **Configuration**: Environment variables and settings
4. **Logging**: Structured logging for monitoring

## Monitoring

The pipeline provides several monitoring capabilities:

- **Status Checks**: Verify both NewsAPI and Pinecone connectivity
- **Processing Statistics**: Track articles fetched, processed, and failed
- **Timestamps**: Track when processing occurred
- **Detailed Logs**: Comprehensive logging for debugging

## Best Practices

1. **Rate Limiting**: Be mindful of NewsAPI rate limits
2. **Error Handling**: Always check the success field in responses
3. **Resource Cleanup**: Call `pipeline.close()` when done
4. **Monitoring**: Regularly check pipeline status
5. **Batch Processing**: Use batch mode for multiple topics to improve efficiency

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set
2. **Network Issues**: Check connectivity to NewsAPI and Pinecone
3. **Rate Limits**: Monitor NewsAPI usage to avoid rate limiting
4. **Pinecone Errors**: Verify Pinecone index configuration and permissions

### Debug Mode

Enable debug logging to get more detailed information:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
``` 