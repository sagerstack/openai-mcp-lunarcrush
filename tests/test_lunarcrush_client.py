"""
Comprehensive unit tests for the LunarCrush Client.

This module tests all components of the LunarCrushClient including:
- Data model validation (CurrentSocialMetrics, MomentumMetrics, SocialMetrics)
- TokenBucket rate limiting algorithm
- API methods with various inputs and edge cases
- Error handling for API failures
- Caching behavior
- Retry logic with exponential backoff
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal

import requests
import responses

from src.lunarcrush_client import (
    LunarCrushClient,
    CurrentSocialMetrics,
    MomentumMetrics,
    SocialMetrics,
    TokenBucket
)
from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushRateLimitError,
    LunarCrushAuthenticationError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestCurrentSocialMetrics:
    """Test cases for CurrentSocialMetrics data model validation."""

    def test_valid_current_metrics_creation(self):
        """Test creating CurrentSocialMetrics with valid data."""
        metrics = CurrentSocialMetrics(
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
        
        assert metrics.symbol == "BTC"
        assert metrics.interactions_24h == 150000
        assert metrics.social_volume_24h == 2500
        assert metrics.social_dominance == 25.5
        assert metrics.galaxy_score == 75.2
        assert metrics.galaxy_score_previous == 73.8
        assert metrics.sentiment == 65.3
        assert metrics.alt_rank == 1
        assert metrics.alt_rank_previous == 2

    def test_current_metrics_with_optional_fields_none(self):
        """Test creating CurrentSocialMetrics with optional fields as None."""
        metrics = CurrentSocialMetrics(
            symbol="ETH",
            interactions_24h=120000,
            social_volume_24h=2100,
            social_dominance=18.7,
            galaxy_score=68.9,
            sentiment=58.2,
            alt_rank=2
        )
        
        assert metrics.galaxy_score_previous is None
        assert metrics.alt_rank_previous is None

    def test_current_metrics_validation_empty_symbol(self):
        """Test validation fails with empty symbol."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=75.2,
                sentiment=65.3,
                alt_rank=1
            )
        
        assert "symbol must be a non-empty string" in str(exc_info.value)

    def test_current_metrics_validation_negative_interactions(self):
        """Test validation fails with negative interactions."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=-100,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=75.2,
                sentiment=65.3,
                alt_rank=1
            )
        
        assert "interactions_24h must be >= 0" in str(exc_info.value)

    def test_current_metrics_validation_negative_social_volume(self):
        """Test validation fails with negative social volume."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=-100,
                social_dominance=25.5,
                galaxy_score=75.2,
                sentiment=65.3,
                alt_rank=1
            )
        
        assert "social_volume_24h must be >= 0" in str(exc_info.value)

    def test_current_metrics_validation_invalid_social_dominance(self):
        """Test validation fails with social dominance out of range."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=150.0,  # Over 100
                galaxy_score=75.2,
                sentiment=65.3,
                alt_rank=1
            )
        
        assert "social_dominance must be between 0 and 100" in str(exc_info.value)

    def test_current_metrics_validation_invalid_galaxy_score(self):
        """Test validation fails with galaxy score out of range."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=-10.0,  # Negative
                sentiment=65.3,
                alt_rank=1
            )
        
        assert "galaxy_score must be between 0 and 100" in str(exc_info.value)

    def test_current_metrics_validation_invalid_galaxy_score_previous(self):
        """Test validation fails with previous galaxy score out of range."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=75.2,
                galaxy_score_previous=150.0,  # Over 100
                sentiment=65.3,
                alt_rank=1
            )
        
        assert "galaxy_score_previous must be between 0 and 100" in str(exc_info.value)

    def test_current_metrics_validation_invalid_sentiment(self):
        """Test validation fails with sentiment out of range."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=75.2,
                sentiment=150.0,  # Over 100
                alt_rank=1
            )
        
        assert "sentiment must be between 0 and 100" in str(exc_info.value)

    def test_current_metrics_validation_invalid_alt_rank(self):
        """Test validation fails with alt rank less than 1."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=75.2,
                sentiment=65.3,
                alt_rank=0  # Invalid
            )
        
        assert "alt_rank must be >= 1" in str(exc_info.value)

    def test_current_metrics_validation_invalid_alt_rank_previous(self):
        """Test validation fails with previous alt rank less than 1."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            CurrentSocialMetrics(
                symbol="BTC",
                interactions_24h=150000,
                social_volume_24h=2500,
                social_dominance=25.5,
                galaxy_score=75.2,
                sentiment=65.3,
                alt_rank=1,
                alt_rank_previous=0  # Invalid
            )
        
        assert "alt_rank_previous must be >= 1" in str(exc_info.value)

    def test_current_metrics_to_dict(self):
        """Test converting CurrentSocialMetrics to dictionary."""
        metrics = CurrentSocialMetrics(
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
        
        result = metrics.to_dict()
        
        assert result["symbol"] == "BTC"
        assert result["interactions_24h"] == 150000
        assert result["social_volume_24h"] == 2500
        assert result["social_dominance"] == 25.5
        assert result["galaxy_score"] == 75.2
        assert result["galaxy_score_previous"] == 73.8
        assert result["sentiment"] == 65.3
        assert result["alt_rank"] == 1
        assert result["alt_rank_previous"] == 2


class TestMomentumMetrics:
    """Test cases for MomentumMetrics data model validation."""

    def test_valid_momentum_metrics_creation(self):
        """Test creating MomentumMetrics with valid data."""
        momentum = MomentumMetrics(
            symbol="BTC",
            galaxy_score_trend=1.4,
            alt_rank_trend=1.0,
            sentiment_trend=5.2,
            interactions_trend=15.5,
            social_dominance_trend=8.3,
            volume_trend=12.0
        )
        
        assert momentum.symbol == "BTC"
        assert momentum.galaxy_score_trend == 1.4
        assert momentum.alt_rank_trend == 1.0
        assert momentum.sentiment_trend == 5.2
        assert momentum.interactions_trend == 15.5
        assert momentum.social_dominance_trend == 8.3
        assert momentum.volume_trend == 12.0

    def test_momentum_metrics_default_values(self):
        """Test creating MomentumMetrics with default values."""
        momentum = MomentumMetrics(symbol="ETH")
        
        assert momentum.symbol == "ETH"
        assert momentum.galaxy_score_trend == 0.0
        assert momentum.alt_rank_trend == 0.0
        assert momentum.sentiment_trend == 0.0
        assert momentum.interactions_trend == 0.0
        assert momentum.social_dominance_trend == 0.0
        assert momentum.volume_trend == 0.0

    def test_momentum_metrics_validation_empty_symbol(self):
        """Test validation fails with empty symbol."""
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            MomentumMetrics(symbol="")
        
        assert "symbol must be a non-empty string" in str(exc_info.value)

    def test_momentum_metrics_to_dict(self):
        """Test converting MomentumMetrics to dictionary."""
        momentum = MomentumMetrics(
            symbol="BTC",
            galaxy_score_trend=1.4,
            alt_rank_trend=1.0,
            sentiment_trend=5.2,
            interactions_trend=15.5,
            social_dominance_trend=8.3,
            volume_trend=12.0
        )
        
        result = momentum.to_dict()
        
        assert result["symbol"] == "BTC"
        assert result["galaxy_score_trend"] == 1.4
        assert result["alt_rank_trend"] == 1.0
        assert result["sentiment_trend"] == 5.2
        assert result["interactions_trend"] == 15.5
        assert result["social_dominance_trend"] == 8.3
        assert result["volume_trend"] == 12.0


class TestSocialMetrics:
    """Test cases for SocialMetrics unified data model."""

    def test_valid_social_metrics_creation(self, current_metrics_btc, momentum_metrics_btc):
        """Test creating SocialMetrics with valid data."""
        timestamp = datetime.now()
        social_metrics = SocialMetrics(
            symbol="BTC",
            current_metrics=current_metrics_btc,
            momentum_metrics=momentum_metrics_btc,
            timestamp=timestamp
        )
        
        assert social_metrics.symbol == "BTC"
        assert social_metrics.current_metrics == current_metrics_btc
        assert social_metrics.momentum_metrics == momentum_metrics_btc
        assert social_metrics.timestamp == timestamp

    def test_social_metrics_default_timestamp(self, current_metrics_btc, momentum_metrics_btc):
        """Test creating SocialMetrics with default timestamp."""
        before = datetime.now()
        social_metrics = SocialMetrics(
            symbol="BTC",
            current_metrics=current_metrics_btc,
            momentum_metrics=momentum_metrics_btc
        )
        after = datetime.now()
        
        assert before <= social_metrics.timestamp <= after

    def test_social_metrics_symbol_mismatch_validation(self, current_metrics_btc):
        """Test validation fails with symbol mismatch."""
        eth_momentum = MomentumMetrics(symbol="ETH")
        
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            SocialMetrics(
                symbol="BTC",
                current_metrics=current_metrics_btc,
                momentum_metrics=eth_momentum
            )
        
        assert "Symbol mismatch between current and momentum metrics" in str(exc_info.value)

    def test_social_metrics_to_dict(self, current_metrics_btc, momentum_metrics_btc):
        """Test converting SocialMetrics to dictionary."""
        timestamp = datetime.now()
        social_metrics = SocialMetrics(
            symbol="BTC",
            current_metrics=current_metrics_btc,
            momentum_metrics=momentum_metrics_btc,
            timestamp=timestamp
        )
        
        result = social_metrics.to_dict()
        
        assert result["symbol"] == "BTC"
        assert result["current_metrics"] == current_metrics_btc.to_dict()
        assert result["momentum_metrics"] == momentum_metrics_btc.to_dict()
        assert result["timestamp"] == timestamp.isoformat()


class TestTokenBucket:
    """Test cases for TokenBucket rate limiting algorithm."""

    def test_token_bucket_initialization(self):
        """Test TokenBucket initialization."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        assert bucket.capacity == 10
        assert bucket.tokens == 10
        assert bucket.refill_rate == 1.0
        assert bucket.last_refill > 0

    def test_token_bucket_consume_success(self):
        """Test successful token consumption."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        result = bucket.consume(5)
        
        assert result is True
        assert bucket.tokens == 5

    def test_token_bucket_consume_insufficient_tokens(self):
        """Test token consumption with insufficient tokens."""
        bucket = TokenBucket(capacity=5, refill_rate=0.0)  # No refill
        
        # Consume all tokens
        assert bucket.consume(5) is True
        assert bucket.tokens == 0
        
        # Try to consume more
        assert bucket.consume(1) is False
        assert bucket.tokens == 0

    def test_token_bucket_refill_over_time(self):
        """Test token refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens per second
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0
        
        # Wait for refill
        time.sleep(0.2)  # Should refill 2 tokens
        
        result = bucket.consume(2)
        assert result is True
        assert bucket.tokens >= 0

    def test_token_bucket_wait_for_token(self):
        """Test waiting for tokens to become available."""
        bucket = TokenBucket(capacity=5, refill_rate=10.0)
        
        # Consume all tokens
        bucket.consume(5)
        
        start_time = time.time()
        bucket.wait_for_token(1)  # Should wait for refill
        elapsed = time.time() - start_time
        
        # Should wait approximately 0.1 seconds for 1 token at 10 tokens/sec
        assert 0.05 <= elapsed <= 0.2

    def test_token_bucket_thread_safety(self):
        """Test TokenBucket thread safety."""
        import threading
        
        bucket = TokenBucket(capacity=100, refill_rate=10.0)  # Allow refill during test
        results = []
        
        def consume_tokens():
            for _ in range(20):  # More attempts to account for refill timing
                result = bucket.consume(1)
                results.append(result)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=consume_tokens)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have at least 100 successful consumptions (initial capacity)
        successful_consumptions = sum(results)
        assert successful_consumptions >= 100


class TestLunarCrushClient:
    """Test cases for LunarCrushClient API methods."""

    def test_client_initialization_with_api_key(self, mock_api_key):
        """Test client initialization with provided API key."""
        client = LunarCrushClient(api_key=mock_api_key)
        
        assert client.api_key == mock_api_key
        assert client.base_url == "https://lunarcrush.com/api4/public"
        assert client.cache_ttl == 300
        assert isinstance(client.rate_limiter, TokenBucket)

    def test_client_initialization_without_api_key(self, monkeypatch):
        """Test client initialization fails without API key."""
        monkeypatch.delenv("LUNARCRUSH_API_KEY", raising=False)
        
        with pytest.raises(LunarCrushAuthenticationError) as exc_info:
            LunarCrushClient()
        
        assert "API key not provided" in str(exc_info.value)

    def test_client_initialization_from_environment(self, monkeypatch, mock_api_key):
        """Test client initialization loads API key from environment."""
        monkeypatch.setenv("LUNARCRUSH_API_KEY", mock_api_key)
        
        client = LunarCrushClient()
        
        assert client.api_key == mock_api_key

    def test_get_cache_key(self, lunarcrush_client):
        """Test cache key generation."""
        key1 = lunarcrush_client._get_cache_key("/test", {"param": "value"})
        key2 = lunarcrush_client._get_cache_key("/test", {"param": "value"})
        key3 = lunarcrush_client._get_cache_key("/test", {"param": "other"})
        
        assert key1 == key2
        assert key1 != key3

    def test_cache_validity_check(self, lunarcrush_client):
        """Test cache validity checking."""
        # Initially invalid
        assert lunarcrush_client._is_cache_valid("nonexistent") is False
        
        # Add to cache
        lunarcrush_client.cache["test"] = "data"
        lunarcrush_client.cache_timestamps["test"] = time.time()
        
        # Should be valid
        assert lunarcrush_client._is_cache_valid("test") is True
        
        # Expire cache
        lunarcrush_client.cache_timestamps["test"] = time.time() - lunarcrush_client.cache_ttl - 1
        
        # Should be invalid
        assert lunarcrush_client._is_cache_valid("test") is False

    @responses.activate
    def test_get_current_metrics_success(self, lunarcrush_client, mock_lunarcrush_response, mock_symbols):
        """Test successful current metrics retrieval."""
        # Mock API response
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/list/v1",
            json=mock_lunarcrush_response,
            status=200
        )
        
        result = lunarcrush_client.get_current_metrics(mock_symbols)
        
        assert len(result) == 3
        assert "BTC" in result
        assert "ETH" in result
        assert "ADA" in result
        
        btc_metrics = result["BTC"]
        assert isinstance(btc_metrics, CurrentSocialMetrics)
        assert btc_metrics.symbol == "BTC"
        assert btc_metrics.interactions_24h == 150000

    @responses.activate
    def test_get_current_metrics_caching(self, lunarcrush_client, mock_lunarcrush_response, mock_symbols):
        """Test that current metrics are cached."""
        # Mock API response
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/list/v1",
            json=mock_lunarcrush_response,
            status=200
        )
        
        # First call should make API request
        result1 = lunarcrush_client.get_current_metrics(mock_symbols)
        assert len(responses.calls) == 1
        
        # Second call should use cache
        result2 = lunarcrush_client.get_current_metrics(mock_symbols)
        assert len(responses.calls) == 1  # No additional calls
        
        assert result1 == result2

    @responses.activate
    def test_get_current_metrics_missing_data_field(self, lunarcrush_client, mock_symbols):
        """Test handling of response missing data field."""
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/list/v1",
            json={"error": "Invalid request"},
            status=200
        )
        
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            lunarcrush_client.get_current_metrics(mock_symbols)
        
        assert "Response missing 'data' field" in str(exc_info.value)

    @responses.activate
    def test_get_current_metrics_partial_symbols(self, lunarcrush_client, mock_lunarcrush_response):
        """Test handling when not all symbols are found."""
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/list/v1",
            json=mock_lunarcrush_response,
            status=200
        )
        
        # Request more symbols than in response
        symbols = ["BTC", "ETH", "ADA", "DOGE"]
        result = lunarcrush_client.get_current_metrics(symbols)
        
        assert len(result) == 3  # Only found symbols
        assert "DOGE" not in result

    @responses.activate
    def test_get_historical_metrics_success(self, lunarcrush_client, mock_historical_response):
        """Test successful historical metrics retrieval."""
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/BTC/time-series/v2",
            json=mock_historical_response,
            status=200
        )
        
        result = lunarcrush_client.get_historical_metrics("BTC")
        
        assert isinstance(result, list)
        assert len(result) == 24  # 24 hourly data points
        assert "time" in result[0]
        assert "interactions" in result[0]

    @responses.activate
    def test_get_historical_metrics_caching(self, lunarcrush_client, mock_historical_response):
        """Test that historical metrics are cached."""
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/BTC/time-series/v2",
            json=mock_historical_response,
            status=200
        )
        
        # First call should make API request
        result1 = lunarcrush_client.get_historical_metrics("BTC")
        assert len(responses.calls) == 1
        
        # Second call should use cache
        result2 = lunarcrush_client.get_historical_metrics("BTC")
        assert len(responses.calls) == 1  # No additional calls
        
        assert result1 == result2

    @responses.activate
    def test_get_historical_metrics_missing_data_field(self, lunarcrush_client):
        """Test handling of historical response missing data field."""
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/BTC/time-series/v2",
            json={"error": "Invalid request"},
            status=200
        )
        
        with pytest.raises(LunarCrushDataValidationError) as exc_info:
            lunarcrush_client.get_historical_metrics("BTC")
        
        assert "Response missing 'data' field" in str(exc_info.value)

    def test_calculate_percentage_changes_with_data(self, lunarcrush_client, current_metrics_btc, mock_historical_response):
        """Test percentage change calculation with historical data."""
        historical_data = mock_historical_response["data"]
        
        result = lunarcrush_client.calculate_percentage_changes(current_metrics_btc, historical_data)
        
        assert isinstance(result, MomentumMetrics)
        assert result.symbol == "BTC"
        assert result.interactions_trend > 0  # Should have positive trend
        assert result.volume_trend > 0

    def test_calculate_percentage_changes_empty_historical(self, lunarcrush_client, current_metrics_btc):
        """Test percentage change calculation with empty historical data."""
        result = lunarcrush_client.calculate_percentage_changes(current_metrics_btc, [])
        
        assert isinstance(result, MomentumMetrics)
        assert result.symbol == "BTC"
        assert result.galaxy_score_trend == 0.0
        assert result.alt_rank_trend == 0.0

    def test_calculate_percentage_changes_zero_historical_values(self, lunarcrush_client, current_metrics_btc):
        """Test percentage change calculation with zero historical values."""
        historical_data = [
            {
                "time": int(datetime.now().timestamp()),
                "interactions": 0,
                "posts_active": 0,
                "sentiment": 0,
                "social_dominance": 0.0
            }
        ]
        
        result = lunarcrush_client.calculate_percentage_changes(current_metrics_btc, historical_data)
        
        assert isinstance(result, MomentumMetrics)
        assert result.symbol == "BTC"
        # Should use current values when historical is zero
        assert result.interactions_trend == current_metrics_btc.interactions_24h
        assert result.volume_trend == current_metrics_btc.social_volume_24h

    def test_calculate_percentage_changes_galaxy_score_change(self, lunarcrush_client, current_metrics_btc):
        """Test galaxy score change calculation."""
        historical_data = [{"time": int(datetime.now().timestamp())}]
        
        result = lunarcrush_client.calculate_percentage_changes(current_metrics_btc, historical_data)
        
        # Should use direct subtraction for galaxy score
        expected_change = current_metrics_btc.galaxy_score - current_metrics_btc.galaxy_score_previous
        assert result.galaxy_score_trend == expected_change

    def test_calculate_percentage_changes_alt_rank_change(self, lunarcrush_client, current_metrics_btc):
        """Test alt rank change calculation."""
        historical_data = [{"time": int(datetime.now().timestamp())}]
        
        result = lunarcrush_client.calculate_percentage_changes(current_metrics_btc, historical_data)
        
        # Should use reverse subtraction for alt rank (lower is better)
        expected_change = current_metrics_btc.alt_rank_previous - current_metrics_btc.alt_rank
        assert result.alt_rank_trend == expected_change

    def test_calculate_percentage_changes_no_previous_values(self, lunarcrush_client, current_metrics_btc):
        """Test percentage change calculation with no previous values."""
        # Create metrics without previous values
        current_no_prev = CurrentSocialMetrics(
            symbol="BTC",
            interactions_24h=150000,
            social_volume_24h=2500,
            social_dominance=25.5,
            galaxy_score=75.2,
            sentiment=65.3,
            alt_rank=1
        )
        
        historical_data = [{"time": int(datetime.now().timestamp())}]
        
        result = lunarcrush_client.calculate_percentage_changes(current_no_prev, historical_data)
        
        assert result.galaxy_score_trend == 0.0
        assert result.alt_rank_trend == 0.0

    @responses.activate
    def test_get_comprehensive_metrics_success(self, lunarcrush_client, mock_lunarcrush_response, mock_historical_response, mock_symbols):
        """Test successful comprehensive metrics retrieval."""
        # Mock API responses
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/list/v1",
            json=mock_lunarcrush_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/BTC/time-series/v2",
            json=mock_historical_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/ETH/time-series/v2",
            json=mock_historical_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://lunarcrush.com/api4/public/coins/ADA/time-series/v2",
            json=mock_historical_response,
            status=200
        )
        
        result = lunarcrush_client.get_comprehensive_metrics(mock_symbols)
        
        assert len(result) == 3
        for metrics in result:
            assert isinstance(metrics, SocialMetrics)
            assert metrics.symbol in mock_symbols
            assert isinstance(metrics.current_metrics, CurrentSocialMetrics)
            assert isinstance(metrics.momentum_metrics, MomentumMetrics)

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_success(self, mock_request, lunarcrush_client):
        """Test successful request with retry logic."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response
        
        result = lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert result == {"data": "test"}
        mock_request.assert_called_once()

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_authentication_error(self, mock_request, lunarcrush_client):
        """Test handling of authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_request.return_value = mock_response
        
        with pytest.raises(LunarCrushAuthenticationError) as exc_info:
            lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert "Invalid API key" in str(exc_info.value)

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_rate_limit_error(self, mock_request, lunarcrush_client):
        """Test handling of rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_request.return_value = mock_response
        
        with pytest.raises(LunarCrushRateLimitError) as exc_info:
            lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert exc_info.value.retry_after == 60

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_server_error(self, mock_request, lunarcrush_client):
        """Test handling of server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_request.return_value = mock_response
        
        with pytest.raises(LunarCrushNetworkError) as exc_info:
            lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert "Server error: 500" in str(exc_info.value)

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_client_error(self, mock_request, lunarcrush_client):
        """Test handling of client error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad request"}
        mock_request.return_value = mock_response
        
        with pytest.raises(LunarCrushAPIError) as exc_info:
            lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert "Client error: 400" in str(exc_info.value)

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_network_error(self, mock_request, lunarcrush_client):
        """Test handling of network error with retry."""
        import requests
        
        # First two attempts fail, third succeeds
        mock_request.side_effect = [
            requests.ConnectionError("Connection failed"),
            requests.ConnectionError("Connection failed"),
            Mock(status_code=200, json=lambda: {"data": "success"})
        ]
        
        result = lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert result == {"data": "success"}
        assert mock_request.call_count == 3

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_max_retries_exceeded(self, mock_request, lunarcrush_client):
        """Test handling when max retries are exceeded."""
        import requests
        
        mock_request.side_effect = requests.ConnectionError("Connection failed")
        
        with pytest.raises(LunarCrushNetworkError) as exc_info:
            lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        assert "Network error after 3 retries" in str(exc_info.value)
        assert mock_request.call_count == 4  # Initial + 3 retries

    @patch('src.lunarcrush_client.requests.Session.request')
    def test_make_request_with_retry_exponential_backoff(self, mock_request, lunarcrush_client):
        """Test exponential backoff in retry logic."""
        import requests
        import time
        
        mock_request.side_effect = [
            requests.ConnectionError("Connection failed"),
            requests.ConnectionError("Connection failed"),
            requests.ConnectionError("Connection failed"),
            requests.ConnectionError("Connection failed")
        ]
        
        start_time = time.time()
        
        with pytest.raises(LunarCrushNetworkError):
            lunarcrush_client._make_request_with_retry("GET", "http://test.com")
        
        elapsed = time.time() - start_time
        
        # Should have waited with exponential backoff
        # Expected delays: ~1s, ~2s, ~4s = ~7s total
        assert elapsed >= 5  # Allow some tolerance

    def test_rate_limiting_behavior(self, lunarcrush_client):
        """Test that rate limiting is applied to requests."""
        # The rate limiter should be configured for 30 requests per minute
        assert lunarcrush_client.rate_limiter.capacity == 30
        assert lunarcrush_client.rate_limiter.refill_rate == 30 / 60  # 30 requests per 60 seconds

    def test_cache_ttl_configuration(self, mock_api_key):
        """Test custom cache TTL configuration."""
        client = LunarCrushClient(api_key=mock_api_key, cache_ttl=600)
        
        assert client.cache_ttl == 600

    def test_session_configuration(self, lunarcrush_client, mock_api_key):
        """Test HTTP session configuration."""
        assert lunarcrush_client.session.headers["Authorization"] == f"Bearer {mock_api_key}"
        assert lunarcrush_client.session.headers["Content-Type"] == "application/json"