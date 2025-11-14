"""
Pytest configuration and shared fixtures for the LunarCrush test suite.

This module provides common fixtures and configuration for all tests,
including mock objects, test data, and test environment setup.
"""

import os
import json
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

import responses
from moto import mock_s3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lunarcrush_client import (
    LunarCrushClient,
    CurrentSocialMetrics,
    MomentumMetrics,
    SocialMetrics,
    TokenBucket
)
from src.adapters.s3_storage import S3Storage
from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushRateLimitError,
    LunarCrushAuthenticationError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)


@pytest.fixture
def mock_api_key():
    """Fixture providing a mock API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def mock_symbols():
    """Fixture providing a list of test cryptocurrency symbols."""
    return ["BTC", "ETH", "ADA"]


@pytest.fixture
def mock_lunarcrush_response():
    """Fixture providing a mock LunarCrush API response."""
    return {
        "data": [
            {
                "symbol": "BTC",
                "interactions_24h": 150000,
                "social_volume_24h": 2500,
                "social_dominance": 25.5,
                "galaxy_score": 75.2,
                "galaxy_score_previous": 73.8,
                "sentiment": 65.3,
                "alt_rank": 1,
                "alt_rank_previous": 2
            },
            {
                "symbol": "ETH",
                "interactions_24h": 120000,
                "social_volume_24h": 2100,
                "social_dominance": 18.7,
                "galaxy_score": 68.9,
                "galaxy_score_previous": 67.1,
                "sentiment": 58.2,
                "alt_rank": 2,
                "alt_rank_previous": 3
            },
            {
                "symbol": "ADA",
                "interactions_24h": 80000,
                "social_volume_24h": 1500,
                "social_dominance": 12.3,
                "galaxy_score": 62.4,
                "galaxy_score_previous": 61.0,
                "sentiment": 52.8,
                "alt_rank": 8,
                "alt_rank_previous": 7
            }
        ]
    }


@pytest.fixture
def mock_historical_response():
    """Fixture providing a mock historical data response."""
    now = datetime.now()
    historical_data = []
    
    # Generate 24 hourly data points
    for i in range(24):
        timestamp = now - timedelta(hours=i)
        historical_data.append({
            "time": int(timestamp.timestamp()),
            "interactions": 100000 + (i * 1000),
            "posts_active": 2000 + (i * 50),
            "sentiment": 60.0 + (i * 0.5),
            "social_dominance": 20.0 + (i * 0.2)
        })
    
    return {"data": historical_data}


@pytest.fixture
def current_metrics_btc():
    """Fixture providing a CurrentSocialMetrics object for BTC."""
    return CurrentSocialMetrics(
        symbol="BTC",
        interactions_24h=150000,
        social_volume_24h=2500,
        social_dominance=25.5,
        galaxy_score=75.2,
        galaxy_score_previous=73.8,
        sentiment=65.3,
        alt_rank=1,
        alt_rank_previous=2
    )


@pytest.fixture
def momentum_metrics_btc():
    """Fixture providing a MomentumMetrics object for BTC."""
    return MomentumMetrics(
        symbol="BTC",
        galaxy_score_trend=1.4,
        alt_rank_trend=1.0,
        sentiment_trend=5.2,
        interactions_trend=15.5,
        social_dominance_trend=8.3,
        volume_trend=12.0
    )


@pytest.fixture
def social_metrics_btc(current_metrics_btc, momentum_metrics_btc):
    """Fixture providing a SocialMetrics object for BTC."""
    return SocialMetrics(
        symbol="BTC",
        current_metrics=current_metrics_btc,
        momentum_metrics=momentum_metrics_btc,
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_lambda_event():
    """Fixture providing a mock Lambda event."""
    return {
        "body": json.dumps({
            "symbols": ["BTC", "ETH", "ADA"],
            "parameters": {
                "include_historical": True
            }
        }),
        "httpMethod": "POST",
        "headers": {
            "Content-Type": "application/json"
        }
    }


@pytest.fixture
def mock_lambda_context():
    """Fixture providing a mock Lambda context."""
    context = Mock()
    context.aws_request_id = "test-request-id-12345"
    context.function_name = "test-lunarcrush-function"
    context.function_version = "1.0"
    return context


@pytest.fixture
def mock_environment_variables(monkeypatch):
    """Fixture setting up required environment variables for testing."""
    monkeypatch.setenv("LUNARCRUSH_API_KEY", "test_api_key_12345")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def lunarcrush_client(mock_api_key):
    """Fixture providing a LunarCrushClient instance for testing."""
    return LunarCrushClient(api_key=mock_api_key, cache_ttl=60)


@pytest.fixture
def token_bucket():
    """Fixture providing a TokenBucket instance for testing."""
    return TokenBucket(capacity=10, refill_rate=1.0)


@pytest.fixture
@mock_s3
def s3_storage():
    """Fixture providing an S3Storage instance with mocked S3."""
    import boto3
    from moto import mock_s3
    
    with mock_s3():
        # Create a mock bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        
        return S3Storage(
            bucket_name="test-bucket",
            aws_region="us-east-1"
        )


@pytest.fixture
def responses_mock():
    """Fixture providing a responses mock for HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sample_metrics_data():
    """Fixture providing sample metrics data for testing."""
    return [
        {
            "symbol": "BTC",
            "current": {
                "interactions_24h": 150000,
                "social_volume_24h": 2500,
                "social_dominance": 25.5,
                "galaxy_score": 75.2,
                "galaxy_score_previous": 73.8,
                "sentiment": 65.3,
                "alt_rank": 1,
                "alt_rank_previous": 2
            },
            "changes": {
                "interactions_24h_pct": 15.5,
                "social_volume_24h_pct": 12.0,
                "social_dominance_pct": 8.3,
                "galaxy_score_change": 1.4,
                "sentiment_pct": 5.2,
                "alt_rank_change": 1.0
            },
            "timestamp": datetime.now().isoformat()
        },
        {
            "symbol": "ETH",
            "current": {
                "interactions_24h": 120000,
                "social_volume_24h": 2100,
                "social_dominance": 18.7,
                "galaxy_score": 68.9,
                "galaxy_score_previous": 67.1,
                "sentiment": 58.2,
                "alt_rank": 2,
                "alt_rank_previous": 3
            },
            "changes": {
                "interactions_24h_pct": 12.3,
                "social_volume_24h_pct": 10.5,
                "social_dominance_pct": 6.7,
                "galaxy_score_change": 1.8,
                "sentiment_pct": 4.1,
                "alt_rank_change": 1.0
            },
            "timestamp": datetime.now().isoformat()
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Fixture to clean up cache between tests."""
    yield
    # Clean up any cache after each test
    import time
    from src.lunarcrush_client import LunarCrushClient
    # This will be called after each test


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )


# Helper functions for tests
def create_mock_response(status_code=200, json_data=None, headers=None):
    """Helper function to create mock HTTP responses."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    mock_response.headers = headers or {}
    mock_response.content = json.dumps(json_data or {}).encode()
    return mock_response


def create_error_response(status_code, error_message, headers=None):
    """Helper function to create mock error responses."""
    return create_mock_response(
        status_code=status_code,
        json_data={"error": error_message},
        headers=headers
    )