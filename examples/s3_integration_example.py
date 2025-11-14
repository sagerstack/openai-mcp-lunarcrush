"""
Example demonstrating S3 storage integration with the Lambda function.

This example shows how to use the S3Storage class to store and retrieve
cryptocurrency metrics data, following the implementation plan requirements.
"""

import os
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.adapters.s3_storage import S3Storage
from src.lunarcrush_client import LunarCrushClient, SocialMetrics, CurrentSocialMetrics, MomentumMetrics


def create_sample_metrics() -> List[SocialMetrics]:
    """Create sample metrics data for demonstration."""
    
    # Sample current metrics
    current_metrics = CurrentSocialMetrics(
        symbol="BTC",
        interactions_24h=1500,
        social_volume_24h=750,
        social_dominance=3.2,
        galaxy_score=82.5,
        galaxy_score_previous=78.0,
        sentiment=0.7,
        alt_rank=1,
        alt_rank_previous=2
    )
    
    # Sample momentum metrics  
    momentum_metrics = MomentumMetrics(
        symbol="BTC",
        galaxy_score_trend=4.5,
        alt_rank_trend=1,
        sentiment_trend=12.0,
        interactions_trend=25.0,
        social_dominance_trend=8.0,
        volume_trend=30.0
    )
    
    # Create unified social metrics
    social_metrics = SocialMetrics(
        symbol="BTC",
        current_metrics=current_metrics,
        momentum_metrics=momentum_metrics,
        timestamp=datetime.now(timezone.utc)
    )
    
    return [social_metrics]


def demonstrate_s3_storage():
    """Demonstrate S3 storage functionality."""
    
    print("=== S3 Storage Integration Example ===\n")
    
    # Initialize S3 storage (for LocalStack development)
    print("1. Initializing S3 storage...")
    try:
        storage = S3Storage(
            bucket_name="test-bucket",
            endpoint_url="http://localhost:4566"  # LocalStack endpoint
        )
        print("✅ S3 storage initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize S3 storage: {e}\n")
        return
    
    # Create sample metrics
    print("2. Creating sample metrics data...")
    metrics = create_sample_metrics()
    print(f"✅ Created {len(metrics)} sample metrics\n")
    
    # Store metrics to S3
    print("3. Storing metrics to S3...")
    try:
        success = storage.store_metrics(metrics)
        if success:
            print("✅ Metrics stored successfully\n")
        else:
            print("❌ Failed to store metrics\n")
            return
    except Exception as e:
        print(f"❌ Error storing metrics: {e}\n")
        return
    
    # Format and display JSON structure
    print("4. Displaying JSON structure...")
    formatted_data = storage.format_metrics_json(metrics)
    print("JSON structure that will be stored in candidates.json:")
    import json
    print(json.dumps(formatted_data, indent=2))
    print()
    
    # Retrieve current metrics
    print("5. Retrieving current metrics from S3...")
    try:
        current_data = storage.get_current_metrics()
        if current_data:
            print("✅ Current metrics retrieved successfully")
            print(f"   Symbols: {current_data.get('metadata', {}).get('symbols', [])}")
            print(f"   Count: {current_data.get('metadata', {}).get('count', 0)}")
        else:
            print("ℹ️  No current metrics found")
    except Exception as e:
        print(f"❌ Error retrieving current metrics: {e}")
    
    print()
    
    # List archive files
    print("6. Listing archive files...")
    try:
        archive_files = storage.list_archive_files()
        if archive_files:
            print(f"✅ Found {len(archive_files)} archive files:")
            for file in archive_files[:5]:  # Show first 5
                print(f"   - {file}")
            if len(archive_files) > 5:
                print(f"   ... and {len(archive_files) - 5} more")
        else:
            print("ℹ️  No archive files found")
    except Exception as e:
        print(f"❌ Error listing archive files: {e}")
    
    print("\n=== Integration Example Complete ===")


def demonstrate_lambda_integration():
    """Demonstrate how S3 storage integrates with Lambda function."""
    
    print("\n=== Lambda Integration Example ===\n")
    
    print("This example shows how S3Storage would be integrated into the Lambda function:")
    print()
    
    integration_code = '''
# In the Lambda function, after fetching metrics:

# Initialize S3 storage
storage = S3Storage(bucket_name=os.getenv("S3_BUCKET_NAME"))

# Store metrics to S3
success = storage.store_metrics(comprehensive_metrics)
if success:
    logger.info("Metrics stored to S3 successfully")
else:
    logger.error("Failed to store metrics to S3")

# The stored JSON structure in candidates.json:
{
  "metrics": [
    {
      "symbol": "BTC",
      "current": {
        "interactions_24h": 1500,
        "social_volume_24h": 750,
        "social_dominance": 3.2,
        "galaxy_score": 82.5,
        "galaxy_score_previous": 78.0,
        "sentiment": 0.7,
        "alt_rank": 1,
        "alt_rank_previous": 2
      },
      "changes": {
        "interactions_24h_pct": 25.0,
        "social_volume_24h_pct": 30.0,
        "social_dominance_pct": 8.0,
        "galaxy_score_change": 4.5,
        "sentiment_pct": 12.0,
        "alt_rank_change": 1
      },
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ],
  "metadata": {
    "count": 1,
    "last_updated": "2025-01-01T12:00:00Z",
    "symbols": ["BTC"]
  }
}
'''
    
    print(integration_code)


if __name__ == "__main__":
    # Check if running in development environment
    if os.getenv("DEVELOPMENT_MODE") or "--dev" in sys.argv:
        demonstrate_s3_storage()
    
    # Always show Lambda integration example
    demonstrate_lambda_integration()