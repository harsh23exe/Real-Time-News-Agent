#!/usr/bin/env python3
"""
Main script to run the news ingestion pipeline.
This script demonstrates how to use the NewsPipeline to fetch news from NewsAPI
and upload to Pinecone database.
"""

import argparse
import sys
from datetime import datetime, timedelta
from services.news_pipeline import NewsPipeline
from utils.logger import logger


def main():
    """Main function to run the news pipeline"""
    parser = argparse.ArgumentParser(description='News Ingestion Pipeline')
    parser.add_argument('--mode', choices=['topic', 'headlines', 'domain', 'batch'], 
                       required=True, help='Pipeline mode to run')
    parser.add_argument('--topics', nargs='+', help='Topics to process (for topic/batch mode)')
    parser.add_argument('--domain', help='Domain to process (for domain mode)')
    parser.add_argument('--country', default='us', help='Country for headlines (default: us)')
    parser.add_argument('--category', help='Category for headlines (optional)')
    parser.add_argument('--from-date', help='From date (YYYY-MM-DD format)')
    parser.add_argument('--language', default='en', help='Language (default: en)')
    parser.add_argument('--sort-by', default='publishedAt', help='Sort by (default: publishedAt)')
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        pipeline = NewsPipeline()
        
        # Check pipeline status
        status = pipeline.get_pipeline_status()
        if not status['success']:
            logger.error("Pipeline status check failed")
            return 1
        
        logger.info("Pipeline status check passed")
        
        # Run pipeline based on mode
        if args.mode == 'topic':
            if not args.topics or len(args.topics) != 1:
                logger.error("Topic mode requires exactly one topic")
                return 1
            
            result = pipeline.process_news_topic(
                topic=args.topics[0],
                from_date=args.from_date,
                language=args.language,
                sort_by=args.sort_by
            )
            
        elif args.mode == 'headlines':
            result = pipeline.process_top_headlines(
                country=args.country,
                category=args.category
            )
            
        elif args.mode == 'domain':
            if not args.domain:
                logger.error("Domain mode requires --domain parameter")
                return 1
            
            result = pipeline.process_domain_news(
                domain=args.domain,
                from_date=args.from_date
            )
            
        elif args.mode == 'batch':
            if not args.topics:
                logger.error("Batch mode requires --topics parameter")
                return 1
            
            result = pipeline.batch_process_topics(
                topics=args.topics,
                from_date=args.from_date
            )
        
        # Print results
        if result['success']:
            logger.info("Pipeline completed successfully!")
            print(f"\n=== Pipeline Results ===")
            print(f"Success: {result['success']}")
            
            if 'articles_fetched' in result:
                print(f"Articles fetched: {result['articles_fetched']}")
            if 'articles_processed' in result:
                print(f"Articles processed: {result['articles_processed']}")
            if 'articles_failed' in result:
                print(f"Articles failed: {result['articles_failed']}")
            if 'total_articles_processed' in result:
                print(f"Total articles processed: {result['total_articles_processed']}")
            if 'total_articles_failed' in result:
                print(f"Total articles failed: {result['total_articles_failed']}")
            
            print(f"Timestamp: {result['timestamp']}")
            
        else:
            logger.error(f"Pipeline failed: {result.get('error', 'Unknown error')}")
            return 1
        
        # Clean up
        pipeline.close()
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return 1


def run_example_pipeline():
    """Run an example pipeline with predefined topics"""
    try:
        logger.info("Running example pipeline...")
        
        pipeline = NewsPipeline()
        
        # Example 1: Process a single topic
        logger.info("Example 1: Processing 'artificial intelligence' topic")
        result1 = pipeline.process_news_topic(
            topic="artificial intelligence",
            from_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        )
        print(f"Result 1: {result1}")
        
        # Example 2: Process top headlines
        logger.info("Example 2: Processing top headlines")
        result2 = pipeline.process_top_headlines(country='us', category='technology')
        print(f"Result 2: {result2}")
        
        # Example 3: Process multiple topics in batch
        logger.info("Example 3: Processing multiple topics in batch")
        topics = ['climate change', 'renewable energy', 'electric vehicles']
        result3 = pipeline.batch_process_topics(
            topics=topics,
            from_date=(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        )
        print(f"Result 3: {result3}")
        
        pipeline.close()
        logger.info("Example pipeline completed")
        
    except Exception as e:
        logger.error(f"Example pipeline failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run example
        sys.exit(run_example_pipeline())
    else:
        # Run with provided arguments
        sys.exit(main()) 