#!/usr/bin/env python3
"""
Example usage of the News Pipeline.
This script demonstrates how to use the NewsPipeline to fetch news from NewsAPI
and upload to Pinecone database.
"""

import os
import sys
from datetime import datetime, timedelta
from services.news_pipeline import NewsPipeline
from utils.logger import logger


def example_single_topic():
    """Example: Process a single topic"""
    print("\n=== Example 1: Single Topic Processing ===")
    
    try:
        pipeline = NewsPipeline()
        
        result = pipeline.process_news_topic(
            topic="artificial intelligence",
            from_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            language="en",
            sort_by="publishedAt"
        )
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Topic: {result['topic']}")
            print(f"Articles fetched: {result['articles_fetched']}")
            print(f"Articles processed: {result['articles_processed']}")
            print(f"Articles failed: {result['articles_failed']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        pipeline.close()
        
    except Exception as e:
        print(f"Error: {e}")


def example_top_headlines():
    """Example: Process top headlines"""
    print("\n=== Example 2: Top Headlines Processing ===")
    
    try:
        pipeline = NewsPipeline()
        
        result = pipeline.process_top_headlines(
            country="us",
            category="technology"
        )
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Country: {result['country']}")
            print(f"Category: {result['category']}")
            print(f"Articles fetched: {result['articles_fetched']}")
            print(f"Articles processed: {result['articles_processed']}")
            print(f"Articles failed: {result['articles_failed']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        pipeline.close()
        
    except Exception as e:
        print(f"Error: {e}")


def example_domain_news():
    """Example: Process news from a specific domain"""
    print("\n=== Example 3: Domain News Processing ===")
    
    try:
        pipeline = NewsPipeline()
        
        result = pipeline.process_domain_news(
            domain="techcrunch.com",
            from_date=(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        )
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Domain: {result['domain']}")
            print(f"Articles fetched: {result['articles_fetched']}")
            print(f"Articles processed: {result['articles_processed']}")
            print(f"Articles failed: {result['articles_failed']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        pipeline.close()
        
    except Exception as e:
        print(f"Error: {e}")


def example_batch_processing():
    """Example: Batch process multiple topics"""
    print("\n=== Example 4: Batch Topic Processing ===")
    
    try:
        pipeline = NewsPipeline()
        
        topics = [
            "climate change",
            "renewable energy", 
            "electric vehicles",
            "solar power"
        ]
        
        result = pipeline.batch_process_topics(
            topics=topics,
            from_date=(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        )
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Topics processed: {result['topics_processed']}")
            print(f"Total articles processed: {result['total_articles_processed']}")
            print(f"Total articles failed: {result['total_articles_failed']}")
            print(f"Timestamp: {result['timestamp']}")
            
            print("\nIndividual Results:")
            for i, individual_result in enumerate(result['individual_results']):
                print(f"  Topic {i+1}: {individual_result['topic']}")
                print(f"    Articles processed: {individual_result['articles_processed']}")
                print(f"    Articles failed: {individual_result['articles_failed']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        pipeline.close()
        
    except Exception as e:
        print(f"Error: {e}")


def example_pipeline_status():
    """Example: Check pipeline status"""
    print("\n=== Example 5: Pipeline Status Check ===")
    
    try:
        pipeline = NewsPipeline()
        
        status = pipeline.get_pipeline_status()
        
        print(f"Success: {status['success']}")
        if status['success']:
            print(f"News API Status: {status['news_api_status']}")
            print(f"Pinecone Status: {status['pinecone_status']}")
            print(f"Timestamp: {status['timestamp']}")
        else:
            print(f"Error: {status.get('error', 'Unknown error')}")
        
        pipeline.close()
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples"""
    print("News Pipeline Examples")
    print("=" * 50)
    
    # Check if environment variables are set
    required_vars = ['NEWS_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Some examples may fail without proper API keys.")
        print("Please set the required environment variables before running.")
        print()
    
    # Run examples
    example_pipeline_status()
    example_single_topic()
    example_top_headlines()
    example_domain_news()
    example_batch_processing()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    main() 