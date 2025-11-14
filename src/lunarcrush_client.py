"""LunarCrush API client for fetching cryptocurrency social and market metrics.

This module provides a comprehensive client for interacting with the LunarCrush API v4,
including data models, error handling, and structured logging.
"""

import os
import json
import logging
import time
import threading
import random
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from dotenv import load_dotenv

import requests
import structlog

from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushRateLimitError,
    LunarCrushAuthenticationError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)

# Load environment variables from .env file
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@dataclass
class CurrentSocialMetrics:
    """
    Data class representing current social metrics for a cryptocurrency.

    This model encapsulates the key social and market metrics returned by the
    LunarCrush API for a specific cryptocurrency symbol.
    """

    symbol: str
    interactions_24h: int
    social_volume_24h: int
    social_dominance: float
    galaxy_score: float
    galaxy_score_previous: Optional[float] = None
    sentiment: float = 0.0
    alt_rank: int = 0
    alt_rank_previous: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate the metrics data after initialization."""
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that the data meets expected constraints."""
        errors = []

        if not self.symbol or not isinstance(self.symbol, str):
            errors.append("symbol must be a non-empty string")

        if self.interactions_24h < 0:
            errors.append("interactions_24h must be >= 0")

        if self.social_volume_24h < 0:
            errors.append("social_volume_24h must be >= 0")

        if not (0 <= self.social_dominance <= 100):
            errors.append("social_dominance must be between 0 and 100")

        if not (0 <= self.galaxy_score <= 100):
            errors.append("galaxy_score must be between 0 and 100")

        if self.galaxy_score_previous is not None and not (0 <= self.galaxy_score_previous <= 100):
            errors.append("galaxy_score_previous must be between 0 and 100")

        if not (0 <= self.sentiment <= 100):
            errors.append("sentiment must be between 0 and 100")

        if self.alt_rank < 1:
            errors.append("alt_rank must be >= 1")

        if self.alt_rank_previous is not None and self.alt_rank_previous < 1:
            errors.append("alt_rank_previous must be >= 1")

        if errors:
            # Create a mapping of field names to their actual values
            field_mapping = {
                "symbol must be a non-empty string": "symbol",
                "interactions_24h must be >= 0": "interactions_24h",
                "social_volume_24h must be >= 0": "social_volume_24h",
                "social_dominance must be between 0 and 100": "social_dominance",
                "galaxy_score must be between 0 and 100": "galaxy_score",
                "galaxy_score_previous must be between 0 and 100": "galaxy_score_previous",
                "sentiment must be between 0 and 100": "sentiment",
                "alt_rank must be >= 1": "alt_rank",
                "alt_rank_previous must be >= 1": "alt_rank_previous"
            }
            
            invalid_fields = {}
            for error_msg in errors:
                field_name = field_mapping.get(error_msg)
                if field_name and hasattr(self, field_name):
                    invalid_fields[field_name] = getattr(self, field_name)
            
            raise LunarCrushDataValidationError(
                f"Invalid metrics data: {', '.join(errors)}",
                invalid_fields=invalid_fields
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the data class to a dictionary."""
        return {
            "symbol": self.symbol,
            "interactions_24h": self.interactions_24h,
            "social_volume_24h": self.social_volume_24h,
            "social_dominance": self.social_dominance,
            "galaxy_score": self.galaxy_score,
            "galaxy_score_previous": self.galaxy_score_previous,
            "sentiment": self.sentiment,
            "alt_rank": self.alt_rank,
            "alt_rank_previous": self.alt_rank_previous
        }


@dataclass
class MomentumMetrics:
    """
    Data class representing momentum-based metrics for a cryptocurrency.

    This model encapsulates momentum indicators and trend analysis metrics.
    """

    symbol: str
    galaxy_score_trend: float = 0.0  # Change in galaxy score over time
    alt_rank_trend: float = 0.0      # Change in alt rank over time
    sentiment_trend: float = 0.0     # Change in sentiment over time
    interactions_trend: float = 0.0  # Change in interactions over time
    social_dominance_trend: float = 0.0  # Change in social dominance over time
    volume_trend: float = 0.0        # Change in social volume over time

    def __post_init__(self) -> None:
        """Validate the momentum metrics data after initialization."""
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that the momentum data meets expected constraints."""
        errors = []

        if not self.symbol or not isinstance(self.symbol, str):
            errors.append("symbol must be a non-empty string")

        if errors:
            # Create a mapping of field names to their actual values
            field_mapping = {
                "symbol must be a non-empty string": "symbol"
            }
            
            invalid_fields = {}
            for error_msg in errors:
                field_name = field_mapping.get(error_msg)
                if field_name and hasattr(self, field_name):
                    invalid_fields[field_name] = getattr(self, field_name)
            
            raise LunarCrushDataValidationError(
                f"Invalid momentum data: {', '.join(errors)}",
                invalid_fields=invalid_fields
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the data class to a dictionary."""
        return {
            "symbol": self.symbol,
            "galaxy_score_trend": self.galaxy_score_trend,
            "alt_rank_trend": self.alt_rank_trend,
            "sentiment_trend": self.sentiment_trend,
            "interactions_trend": self.interactions_trend,
            "social_dominance_trend": self.social_dominance_trend,
            "volume_trend": self.volume_trend
        }


@dataclass
class SocialMetrics:
    """
    Unified SocialMetrics class containing both current and momentum-based metrics.

    This class combines current social metrics with momentum indicators to provide
    a comprehensive view of cryptocurrency social performance.
    """

    symbol: str
    current_metrics: CurrentSocialMetrics
    momentum_metrics: MomentumMetrics
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate the unified social metrics data after initialization."""
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate that the unified social metrics data meets expected constraints."""
        if self.current_metrics.symbol != self.momentum_metrics.symbol:
            raise LunarCrushDataValidationError(
                "Symbol mismatch between current and momentum metrics",
                invalid_fields={
                    "current_symbol": self.current_metrics.symbol,
                    "momentum_symbol": self.momentum_metrics.symbol
                }
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the data class to a dictionary."""
        return {
            "symbol": self.symbol,
            "current_metrics": self.current_metrics.to_dict(),
            "momentum_metrics": self.momentum_metrics.to_dict(),
            "timestamp": self.timestamp.isoformat()
        }


class TokenBucket:
    """Token bucket algorithm implementation for rate limiting.

    This class provides thread-safe rate limiting based on the token bucket algorithm,
    which is ideal for API rate limiting scenarios.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """Initialize the token bucket.

        Args:
            capacity: Maximum number of tokens the bucket can hold
            refill_rate: Rate at which tokens are refilled (tokens per second)
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if not enough tokens available
        """
        with self.lock:
            now = time.time()
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_for_token(self, tokens: int = 1) -> None:
        """Wait until tokens are available to consume.

        Args:
            tokens: Number of tokens needed
        """
        while not self.consume(tokens):
            time.sleep(0.1)


class LunarCrushClient:
    """LunarCrush API client for fetching cryptocurrency social and market metrics.

    This client provides a robust interface for extracting current and historical
    social metrics from the LunarCrush API with proper rate limiting, caching,
    and error handling.
    """

    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 300):
        """Initialize the LunarCrush client.

        Args:
            api_key: LunarCrush API key (if None, loads from environment)
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.api_key = api_key or os.getenv("LUNARCRUSH_API_KEY")
        if not self.api_key:
            raise LunarCrushAuthenticationError(
                "API key not provided and not found in environment variables"
            )

        self.base_url = "https://lunarcrush.com/api4/public"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

        # Rate limiting: Conservative approach - 30 requests per minute
        minute_limit = 30
        seconds_per_minute = 60
        self.rate_limiter = TokenBucket(
            capacity=minute_limit,
            refill_rate=minute_limit / seconds_per_minute
        )

        # In-memory cache with 5-minute TTL
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.cache_timestamps = {}

        logger.info("LunarCrush client initialized", rate_limit=minute_limit)

    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        max_retries: int = 3,
        base_delay: float = 2.0
    ) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retry logic.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff

        Returns:
            Response JSON data

        Raises:
            Various LunarCrush exceptions based on error type
        """
        for attempt in range(max_retries + 1):
            try:
                # Apply rate limiting with extra delay
                self.rate_limiter.wait_for_token()
                # Add small delay to be extra conservative
                time.sleep(0.5)

                logger.debug(
                    "Making API request",
                    method=method,
                    url=url,
                    params=params,
                    attempt=attempt + 1
                )

                response = self.session.request(method, url, params=params)

                # Handle HTTP errors
                if response.status_code == 401:
                    raise LunarCrushAuthenticationError(
                        "Invalid API key or authentication failed",
                        response_data=response.json() if response.content else None
                    )
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise LunarCrushRateLimitError(
                        "API rate limit exceeded",
                        retry_after=retry_after,
                        response_data=response.json() if response.content else None
                    )
                elif response.status_code >= 500:
                    raise LunarCrushNetworkError(
                        f"Server error: {response.status_code}"
                    )
                elif response.status_code >= 400:
                    raise LunarCrushAPIError(
                        f"Client error: {response.status_code}",
                        status_code=response.status_code,
                        response_data=response.json() if response.content else None
                    )

                response.raise_for_status()
                return response.json()

            except (requests.RequestException, requests.Timeout) as e:
                if attempt == max_retries:
                    raise LunarCrushNetworkError(
                        f"Network error after {max_retries} retries: {str(e)}",
                        original_exception=e
                    )

                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    "Request failed, retrying",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    delay=delay,
                    error=str(e)
                )
                time.sleep(delay)

        raise LunarCrushNetworkError("Unexpected error in retry logic")

    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key for API requests.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Cache key string
        """
        params_str = json.dumps(params or {}, sort_keys=True)
        return f"{endpoint}:{params_str}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid.

        Args:
            cache_key: Cache key to check

        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.cache_timestamps:
            return False

        cache_age = time.time() - self.cache_timestamps[cache_key]
        return cache_age < self.cache_ttl

    def get_current_metrics(self, symbols: List[str]) -> Dict[str, CurrentSocialMetrics]:
        """Extract current social metrics for specified cryptocurrency symbols.

        Args:
            symbols: List of cryptocurrency symbols to query

        Returns:
            Dictionary mapping symbols to CurrentSocialMetrics objects

        Raises:
            Various LunarCrush exceptions on error
        """
        logger.info("Fetching current metrics", symbols=symbols)

        cache_key = self._get_cache_key("/coins/list/v1", {"symbols": symbols})

        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.debug("Using cached current metrics", symbols=symbols)
            return self.cache[cache_key]

        try:
            # Prepare request parameters - use default ordering to get top coins
            # This ensures we get BTC, ETH, SOL, DOGE, etc. instead of obscure tokens
            params = {
                "limit": max(100, len(symbols) * 3)  # Get more data to ensure we find all symbols
            }

            url = f"{self.base_url}/coins/list/v1"
            response_data = self._make_request_with_retry("GET", url, params)

            # Validate response structure
            if "data" not in response_data:
                raise LunarCrushDataValidationError(
                    "Response missing 'data' field",
                    response_data=response_data
                )

            metrics = {}
            found_symbols = set()

            for coin_data in response_data["data"]:
                symbol = coin_data.get("symbol")
                if symbol and symbol in symbols:
                    found_symbols.add(symbol)

                    # Extract required fields with proper defaults
                    metrics[symbol] = CurrentSocialMetrics(
                        symbol=symbol,
                        interactions_24h=int(coin_data.get("interactions_24h", 0)),
                        social_volume_24h=int(coin_data.get("social_volume_24h", 0)),
                        social_dominance=float(coin_data.get("social_dominance", 0.0)),
                        galaxy_score=float(coin_data.get("galaxy_score", 0.0)),
                        galaxy_score_previous=float(coin_data.get("galaxy_score_previous")) if coin_data.get("galaxy_score_previous") is not None else None,
                        sentiment=float(coin_data.get("sentiment", 0.0)),
                        alt_rank=int(coin_data.get("alt_rank", 0)),
                        alt_rank_previous=int(coin_data.get("alt_rank_previous")) if coin_data.get("alt_rank_previous") is not None else None
                    )

            # Check for missing symbols
            missing_symbols = set(symbols) - found_symbols
            if missing_symbols:
                logger.warning(
                    "Some symbols not found in API response",
                    missing_symbols=list(missing_symbols)
                )

            # Cache the results
            self.cache[cache_key] = metrics
            self.cache_timestamps[cache_key] = time.time()

            logger.info("Current metrics retrieved successfully", symbols_found=list(found_symbols))
            return metrics

        except Exception as e:
            logger.error("Failed to fetch current metrics", error=str(e), symbols=symbols)
            raise

    def get_historical_metrics(self, symbol: str) -> List[Dict[str, Any]]:
        """Extract historical time series data for a cryptocurrency symbol.

        Args:
            symbol: Cryptocurrency symbol to query

        Returns:
            List of historical data points

        Raises:
            Various LunarCrush exceptions on error
        """
        logger.info("Fetching historical metrics", symbol=symbol)

        cache_key = self._get_cache_key(f"/coins/{symbol}/time-series/v2", {})

        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.debug("Using cached historical metrics", symbol=symbol)
            return self.cache[cache_key]

        try:
            # Prepare request parameters for 24-hour data
            params = {
                "bucket": "hour",
                "interval": "1w",  # Use 1 week interval for better data availability
                "start": int((datetime.now() - timedelta(days=7)).timestamp()),
                "end": int(datetime.now().timestamp())
            }

            url = f"{self.base_url}/coins/{symbol}/time-series/v2"
            response_data = self._make_request_with_retry("GET", url, params)

            # Validate response structure
            if "data" not in response_data:
                raise LunarCrushDataValidationError(
                    "Response missing 'data' field",
                    response_data=response_data
                )

            # Cache the results
            self.cache[cache_key] = response_data["data"]
            self.cache_timestamps[cache_key] = time.time()

            logger.info("Historical metrics retrieved successfully", symbol=symbol, data_points=len(response_data["data"]))
            return response_data["data"]

        except Exception as e:
            logger.error("Failed to fetch historical metrics", error=str(e), symbol=symbol)
            raise

    def calculate_percentage_changes(
        self, 
        current: CurrentSocialMetrics, 
        historical_data: List[Dict[str, Any]]
    ) -> MomentumMetrics:
        """Calculate 24-hour percentage changes between current and historical metrics.

        Args:
            current: Current social metrics
            historical_data: Historical time series data

        Returns:
            MomentumMetrics with calculated trends

        Raises:
            LunarCrushDataValidationError if calculation fails
        """
        if not historical_data:
            logger.warning("No historical data available for percentage change calculation", symbol=current.symbol)
            return MomentumMetrics(symbol=current.symbol)

        try:
            # Get the oldest data point (24 hours ago)
            oldest_data = historical_data[0] if historical_data else {}

            # Extract historical values with defaults
            historical_interactions = oldest_data.get("interactions", 0)
            historical_posts_active = oldest_data.get("posts_active", 0)
            historical_sentiment = oldest_data.get("sentiment", 0)
            historical_social_dominance = oldest_data.get("social_dominance", 0.0)

            # Calculate percentage changes using tech research formulas
            interactions_pct = (
                ((current.interactions_24h - historical_interactions) / historical_interactions * 100)
                if historical_interactions > 0 else current.interactions_24h
            )

            social_volume_pct = (
                ((current.social_volume_24h - historical_posts_active) / historical_posts_active * 100)
                if historical_posts_active > 0 else current.social_volume_24h
            )

            social_dominance_pct = (
                ((current.social_dominance - historical_social_dominance) / historical_social_dominance * 100)
                if historical_social_dominance > 0 else current.social_dominance
            )

            sentiment_pct = (
                ((current.sentiment - historical_sentiment) / historical_sentiment * 100)
                if historical_sentiment > 0 else current.sentiment
            )

            # Galaxy score and alt rank use direct subtraction as per tech research
            galaxy_score_change = (
                current.galaxy_score - current.galaxy_score_previous
                if current.galaxy_score_previous is not None else 0.0
            )

            alt_rank_change = (
                current.alt_rank_previous - current.alt_rank
                if current.alt_rank_previous is not None else 0
            )

            momentum = MomentumMetrics(
                symbol=current.symbol,
                galaxy_score_trend=galaxy_score_change,
                alt_rank_trend=alt_rank_change,
                sentiment_trend=sentiment_pct,
                interactions_trend=interactions_pct,
                social_dominance_trend=social_dominance_pct,
                volume_trend=social_volume_pct
            )

            logger.debug(
                "Percentage changes calculated",
                symbol=current.symbol,
                interactions_pct=interactions_pct,
                social_volume_pct=social_volume_pct
            )

            return momentum

        except Exception as e:
            logger.error("Failed to calculate percentage changes", error=str(e), symbol=current.symbol)
            raise LunarCrushDataValidationError(
                f"Failed to calculate percentage changes: {str(e)}",
                invalid_fields={"symbol": current.symbol}
            )

    def get_comprehensive_metrics(self, symbols: List[str]) -> List[SocialMetrics]:
        """Get comprehensive social metrics including current data and percentage changes.

        Args:
            symbols: List of cryptocurrency symbols to query

        Returns:
            List of SocialMetrics with current data and momentum trends
        """
        logger.info("Fetching comprehensive metrics", symbols=symbols)

        try:
            # Get current metrics for all symbols
            current_metrics = self.get_current_metrics(symbols)

            comprehensive_metrics = []

            for symbol, current in current_metrics.items():
                # Get historical data for percentage change calculations
                historical_data = self.get_historical_metrics(symbol)

                # Calculate momentum metrics
                momentum = self.calculate_percentage_changes(current, historical_data)

                # Create comprehensive social metrics object
                social_metrics = SocialMetrics(
                    symbol=symbol,
                    current_metrics=current,
                    momentum_metrics=momentum
                )

                comprehensive_metrics.append(social_metrics)

            logger.info("Comprehensive metrics retrieved successfully", symbols_processed=len(comprehensive_metrics))
            return comprehensive_metrics

        except Exception as e:
            logger.error("Failed to get comprehensive metrics", error=str(e), symbols=symbols)
            raise
