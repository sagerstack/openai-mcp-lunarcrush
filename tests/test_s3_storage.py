"""
Comprehensive unit tests for S3 storage implementation.

This module contains comprehensive unit tests for S3 storage component,
following TDD principles and covering all acceptance criteria from TR-8.
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.adapters.s3_storage import S3Storage
from src.adapters.i_s3_storage import IS3Storage
from src.lunarcrush_client import SocialMetrics, CurrentSocialMetrics, MomentumMetrics
from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestS3Storage:
    """Test cases for S3 storage implementation."""

    @pytest.fixture
    def mock_s3_client(self):
        """Create a mock S3 client for testing."""
        mock_client = Mock()
        return mock_client

    @pytest.fixture
    def sample_metrics(self) -> List[SocialMetrics]:
        """Create sample metrics data for testing."""
        current_metrics = CurrentSocialMetrics(
            symbol="BTC",
            interactions_24h=1000,
            social_volume_24h=500,
            social_dominance=2.5,
            galaxy_score=75.0,
            galaxy_score_previous=70.0,
            sentiment=0.6,
            alt_rank=1,
            alt_rank_previous=2
        )

        momentum_metrics = MomentumMetrics(
            symbol="BTC",
            galaxy_score_trend=5.0,
            alt_rank_trend=1,
            sentiment_trend=10.0,
            interactions_trend=15.0,
            social_dominance_trend=5.0,
            volume_trend=20.0
        )

        social_metrics = SocialMetrics(
            symbol="BTC",
            current_metrics=current_metrics,
            momentum_metrics=momentum_metrics,
            timestamp=datetime.now(timezone.utc)
        )

        return [social_metrics]

    @pytest.fixture
    def multiple_metrics(self) -> List[SocialMetrics]:
        """Create multiple sample metrics for testing."""
        metrics = []
        
        for symbol in ["BTC", "ETH", "ADA"]:
            current = CurrentSocialMetrics(
                symbol=symbol,
                interactions_24h=1000 + len(symbol) * 100,
                social_volume_24h=500 + len(symbol) * 50,
                social_dominance=2.5 + len(symbol) * 0.5,
                galaxy_score=75.0 + len(symbol) * 2,
                galaxy_score_previous=70.0 + len(symbol) * 2,
                sentiment=0.6 + len(symbol) * 0.1,
                alt_rank=1 + len(symbol),
                alt_rank_previous=2 + len(symbol)
            )

            momentum = MomentumMetrics(
                symbol=symbol,
                galaxy_score_trend=5.0 + len(symbol),
                alt_rank_trend=1,
                sentiment_trend=10.0 + len(symbol) * 2,
                interactions_trend=15.0 + len(symbol) * 3,
                social_dominance_trend=5.0 + len(symbol),
                volume_trend=20.0 + len(symbol) * 4
            )

            social = SocialMetrics(
                symbol=symbol,
                current_metrics=current,
                momentum_metrics=momentum,
                timestamp=datetime.now(timezone.utc)
            )
            
            metrics.append(social)
        
        return metrics

    @pytest.fixture
    def s3_storage(self, mock_s3_client):
        """Create S3 storage instance with mocked S3 client."""
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.return_value = {}
            return S3Storage(bucket_name="test-bucket")

    def test_initialization_success(self, mock_s3_client):
        """Test S3 storage initialization success."""
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.return_value = {}

            storage = S3Storage(bucket_name="test-bucket")

            assert storage.bucket_name == "test-bucket"
            assert storage.s3_client == mock_s3_client
            mock_s3_client.head_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_initialization_with_endpoint_url(self, mock_s3_client):
        """Test S3 storage initialization with custom endpoint."""
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.return_value = {}

            endpoint_url = "http://localhost:4566"
            storage = S3Storage(
                bucket_name="test-bucket",
                endpoint_url=endpoint_url
            )

            assert storage.endpoint_url == endpoint_url

    def test_initialization_with_aws_region(self, mock_s3_client):
        """Test S3 storage initialization with custom AWS region."""
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.return_value = {}

            region = "eu-west-1"
            storage = S3Storage(
                bucket_name="test-bucket",
                aws_region=region
            )

            assert storage.aws_region == region

    def test_initialization_from_environment(self, mock_s3_client, monkeypatch):
        """Test S3 storage initialization from environment variables."""
        monkeypatch.setenv("S3_BUCKET_NAME", "env-bucket")
        monkeypatch.setenv("S3_ENDPOINT_URL", "http://localhost:4566")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")

        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.return_value = {}

            storage = S3Storage()

            assert storage.bucket_name == "env-bucket"
            assert storage.endpoint_url == "http://localhost:4566"
            assert storage.aws_region == "us-west-2"

    def test_initialization_missing_bucket_name(self):
        """Test initialization failure when bucket name is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="S3_BUCKET_NAME environment variable is required"):
                S3Storage()

    def test_initialization_no_credentials(self):
        """Test initialization failure when AWS credentials are missing."""
        from botocore.exceptions import NoCredentialsError
        
        with patch('src.adapters.s3_storage.boto3.client') as mock_boto3:
            mock_boto3.side_effect = NoCredentialsError()
            
            with pytest.raises(ValueError, match="AWS credentials not found"):
                S3Storage(bucket_name="test-bucket")

    def test_initialization_connection_failure(self):
        """Test initialization failure when S3 connection fails."""
        with patch('src.adapters.s3_storage.boto3.client') as mock_boto3:
            mock_boto3.side_effect = Exception("Connection failed")
            
            with pytest.raises(LunarCrushNetworkError, match="Failed to initialize S3 client"):
                S3Storage(bucket_name="test-bucket")

    def test_test_connection_success(self, mock_s3_client):
        """Test successful S3 connection test."""
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.return_value = {}

            storage = S3Storage(bucket_name="test-bucket")
            storage._test_connection()

            mock_s3_client.head_bucket.assert_called_with(Bucket="test-bucket")

    def test_test_connection_bucket_not_found(self, mock_s3_client):
        """Test connection test when bucket doesn't exist."""
        from botocore.exceptions import ClientError
        
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.side_effect = ClientError(
                {"Error": {"Code": "404"}}, "HeadBucket"
            )
            
            with pytest.raises(ValueError, match="S3 bucket 'test-bucket' does not exist"):
                S3Storage(bucket_name="test-bucket")

    def test_test_connection_access_denied(self, mock_s3_client):
        """Test connection test when bucket access is denied."""
        from botocore.exceptions import ClientError
        
        with patch('src.adapters.s3_storage.boto3.client', return_value=mock_s3_client):
            mock_s3_client.head_bucket.side_effect = ClientError(
                {"Error": {"Code": "403"}}, "HeadBucket"
            )
            
            with pytest.raises(ValueError, match="No access to S3 bucket 'test-bucket'"):
                S3Storage(bucket_name="test-bucket")

    def test_store_metrics_success(self, s3_storage, sample_metrics, mock_s3_client):
        """Test successful metrics storage."""
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.copy_object.return_value = {}

        result = s3_storage.store_metrics(sample_metrics)

        assert result is True

        # Verify put_object was called with correct parameters
        mock_s3_client.put_object.assert_called_once()
        call_args = mock_s3_client.put_object.call_args

        assert call_args[1]["Bucket"] == "test-bucket"
        assert call_args[1]["Key"] == "candidates.json"
        assert call_args[1]["ContentType"] == "application/json"

        # Verify JSON content structure
        json_content = call_args[1]["Body"].decode("utf-8")
        data = json.loads(json_content)

        assert "metrics" in data
        assert "metadata" in data
        assert data["metadata"]["count"] == 1
        assert data["metadata"]["symbols"] == ["BTC"]

        # Verify metrics structure
        metric_data = data["metrics"][0]
        assert metric_data["symbol"] == "BTC"
        assert "current" in metric_data
        assert "changes" in metric_data
        assert "timestamp" in metric_data

    def test_store_metrics_empty_list(self, s3_storage):
        """Test storing empty metrics list."""
        result = s3_storage.store_metrics([])

        assert result is False
        # Verify put_object was not called
        s3_storage.s3_client.put_object.assert_not_called()

    def test_store_metrics_with_archive(self, s3_storage, sample_metrics, mock_s3_client):
        """Test storing metrics with archiving current file."""
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.copy_object.return_value = {}
        mock_s3_client.head_object.return_value = {}  # Current file exists

        result = s3_storage.store_metrics(sample_metrics)

        assert result is True
        
        # Verify archiving was attempted
        mock_s3_client.copy_object.assert_called_once()
        
        # Verify new file was stored
        mock_s3_client.put_object.assert_called_once()

    def test_store_metrics_archive_failure(self, s3_storage, sample_metrics, mock_s3_client):
        """Test storing metrics when archiving fails."""
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.copy_object.side_effect = Exception("Archive failed")
        mock_s3_client.head_object.return_value = {}  # Current file exists

        result = s3_storage.store_metrics(sample_metrics)

        # Should still succeed despite archive failure
        assert result is True
        
        # Verify new file was stored
        mock_s3_client.put_object.assert_called_once()

    def test_store_metrics_s3_failure(self, s3_storage, sample_metrics, mock_s3_client):
        """Test storing metrics when S3 put_object fails."""
        from botocore.exceptions import ClientError
        
        mock_s3_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal server error"}}, 
            "PutObject"
        )

        with pytest.raises(LunarCrushNetworkError, match="S3 storage failed"):
            s3_storage.store_metrics(sample_metrics)

    def test_store_metrics_unexpected_error(self, s3_storage, sample_metrics, mock_s3_client):
        """Test storing metrics when unexpected error occurs."""
        mock_s3_client.put_object.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(LunarCrushAPIError, match="Failed to store metrics"):
            s3_storage.store_metrics(sample_metrics)

    def test_get_current_metrics_success(self, s3_storage, mock_s3_client):
        """Test successful retrieval of current metrics."""
        sample_response = {
            "metrics": [
                {
                    "symbol": "BTC",
                    "current": {"interactions_24h": 1000},
                    "changes": {"interactions_24h_pct": 15.0},
                    "timestamp": "2025-01-01T00:00:00Z"
                }
            ],
            "metadata": {"count": 1}
        }

        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: json.dumps(sample_response).encode())
        }

        result = s3_storage.get_current_metrics()

        assert result == sample_response
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="candidates.json"
        )

    def test_get_current_metrics_not_found(self, s3_storage, mock_s3_client):
        """Test retrieval when current metrics file doesn't exist."""
        from botocore.exceptions import ClientError
        
        mock_s3_client.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}}, "GetObject"
        )

        result = s3_storage.get_current_metrics()

        assert result is None

    def test_get_current_metrics_s3_error(self, s3_storage, mock_s3_client):
        """Test retrieval when S3 error occurs."""
        from botocore.exceptions import ClientError
        
        mock_s3_client.get_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal server error"}}, 
            "GetObject"
        )

        with pytest.raises(LunarCrushNetworkError, match="Failed to retrieve current metrics"):
            s3_storage.get_current_metrics()

    def test_get_current_metrics_invalid_json(self, s3_storage, mock_s3_client):
        """Test retrieval when JSON is invalid."""
        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: b"invalid json content")
        }

        with pytest.raises(LunarCrushDataValidationError, match="Invalid JSON in current metrics file"):
            s3_storage.get_current_metrics()

    def test_get_current_metrics_unexpected_error(self, s3_storage, mock_s3_client):
        """Test retrieval when unexpected error occurs."""
        mock_s3_client.get_object.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(LunarCrushAPIError, match="Failed to get current metrics"):
            s3_storage.get_current_metrics()

    def test_archive_current_file_success(self, s3_storage, mock_s3_client):
        """Test successful archiving of current file."""
        mock_s3_client.head_object.return_value = {}  # Current file exists
        mock_s3_client.copy_object.return_value = {}

        result = s3_storage.archive_current_file()

        assert result.startswith("archive/candidates_")
        assert result.endswith(".json")
        
        # Verify copy operation
        mock_s3_client.copy_object.assert_called_once()
        call_args = mock_s3_client.copy_object.call_args
        
        assert call_args[1]["Bucket"] == "test-bucket"
        assert call_args[1]["CopySource"]["Bucket"] == "test-bucket"
        assert call_args[1]["CopySource"]["Key"] == "candidates.json"
        assert call_args[1]["Key"].startswith("archive/candidates_")

    def test_archive_current_file_not_exists(self, s3_storage, mock_s3_client):
        """Test archiving when current file doesn't exist."""
        from botocore.exceptions import ClientError
        
        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadObject"
        )

        result = s3_storage.archive_current_file()

        assert result == ""
        mock_s3_client.copy_object.assert_not_called()

    def test_archive_current_file_s3_error(self, s3_storage, mock_s3_client):
        """Test archiving when S3 error occurs."""
        from botocore.exceptions import ClientError
        
        mock_s3_client.head_object.return_value = {}  # File exists
        mock_s3_client.copy_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal server error"}}, 
            "CopyObject"
        )

        with pytest.raises(LunarCrushNetworkError, match="Failed to archive current file"):
            s3_storage.archive_current_file()

    def test_archive_current_file_unexpected_error(self, s3_storage, mock_s3_client):
        """Test archiving when unexpected error occurs."""
        mock_s3_client.head_object.return_value = {}  # File exists
        mock_s3_client.copy_object.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(LunarCrushAPIError, match="Failed to archive current file"):
            s3_storage.archive_current_file()

    def test_list_archive_files_success(self, s3_storage, mock_s3_client):
        """Test successful listing of archive files."""
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        mock_paginator.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "archive/candidates_20250101_120000.json"},
                    {"Key": "archive/candidates_20250101_130000.json"},
                    {"Key": "archive/"}  # Directory entry
                ]
            }
        ]

        result = s3_storage.list_archive_files()

        assert len(result) == 2
        assert "archive/candidates_20250101_120000.json" in result
        assert "archive/candidates_20250101_130000.json" in result
        assert "archive/" not in result  # Directory should be excluded

    def test_list_archive_files_empty(self, s3_storage, mock_s3_client):
        """Test listing when no archive files exist."""
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        mock_paginator.paginate.return_value = [
            {"Contents": []}
        ]

        result = s3_storage.list_archive_files()

        assert result == []

    def test_list_archive_files_no_contents(self, s3_storage, mock_s3_client):
        """Test listing when response has no Contents."""
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        mock_paginator.paginate.return_value = [{}]

        result = s3_storage.list_archive_files()

        assert result == []

    def test_list_archive_files_s3_error(self, s3_storage, mock_s3_client):
        """Test listing when S3 error occurs."""
        from botocore.exceptions import ClientError
        
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        mock_paginator.paginate.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal server error"}}, 
            "ListObjectsV2"
        )

        with pytest.raises(LunarCrushNetworkError, match="Failed to list archive files"):
            s3_storage.list_archive_files()

    def test_list_archive_files_unexpected_error(self, s3_storage, mock_s3_client):
        """Test listing when unexpected error occurs."""
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        mock_paginator.paginate.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(LunarCrushAPIError, match="Failed to list archive files"):
            s3_storage.list_archive_files()

    def test_format_metrics_json_single_metric(self, s3_storage, sample_metrics):
        """Test JSON formatter with single metric."""
        formatted_data = s3_storage.format_metrics_json(sample_metrics)

        # Verify top-level structure
        assert "metrics" in formatted_data
        assert "metadata" in formatted_data

        # Verify metadata
        metadata = formatted_data["metadata"]
        assert metadata["count"] == 1
        assert metadata["symbols"] == ["BTC"]
        assert "last_updated" in metadata

        # Verify metrics structure
        metrics = formatted_data["metrics"]
        assert len(metrics) == 1

        metric = metrics[0]
        assert metric["symbol"] == "BTC"
        assert "current" in metric
        assert "changes" in metric
        assert "timestamp" in metric

    def test_format_metrics_json_multiple_metrics(self, s3_storage, multiple_metrics):
        """Test JSON formatter with multiple metrics."""
        formatted_data = s3_storage.format_metrics_json(multiple_metrics)

        # Verify metadata
        metadata = formatted_data["metadata"]
        assert metadata["count"] == 3
        assert set(metadata["symbols"]) == {"BTC", "ETH", "ADA"}

        # Verify metrics structure
        metrics = formatted_data["metrics"]
        assert len(metrics) == 3

        symbols = [metric["symbol"] for metric in metrics]
        assert set(symbols) == {"BTC", "ETH", "ADA"}

    def test_format_metrics_json_current_structure(self, s3_storage, sample_metrics):
        """Test JSON formatter current metrics structure."""
        formatted_data = s3_storage.format_metrics_json(sample_metrics)
        metric = formatted_data["metrics"][0]
        current = metric["current"]

        # Verify all current metrics fields
        assert "interactions_24h" in current
        assert "social_volume_24h" in current
        assert "social_dominance" in current
        assert "galaxy_score" in current
        assert "galaxy_score_previous" in current
        assert "sentiment" in current
        assert "alt_rank" in current
        assert "alt_rank_previous" in current

        # Verify values
        assert current["interactions_24h"] == 1000
        assert current["social_volume_24h"] == 500
        assert current["social_dominance"] == 2.5
        assert current["galaxy_score"] == 75.0
        assert current["galaxy_score_previous"] == 70.0
        assert current["sentiment"] == 0.6
        assert current["alt_rank"] == 1
        assert current["alt_rank_previous"] == 2

    def test_format_metrics_json_changes_structure(self, s3_storage, sample_metrics):
        """Test JSON formatter changes structure."""
        formatted_data = s3_storage.format_metrics_json(sample_metrics)
        metric = formatted_data["metrics"][0]
        changes = metric["changes"]

        # Verify all change fields
        assert "interactions_24h_pct" in changes
        assert "social_volume_24h_pct" in changes
        assert "social_dominance_pct" in changes
        assert "galaxy_score_change" in changes
        assert "sentiment_pct" in changes
        assert "alt_rank_change" in changes

        # Verify values
        assert changes["interactions_24h_pct"] == 15.0
        assert changes["social_volume_24h_pct"] == 20.0
        assert changes["social_dominance_pct"] == 5.0
        assert changes["galaxy_score_change"] == 5.0
        assert changes["sentiment_pct"] == 10.0
        assert changes["alt_rank_change"] == 1

    def test_format_metrics_json_timestamp_format(self, s3_storage, sample_metrics):
        """Test JSON formatter timestamp format."""
        formatted_data = s3_storage.format_metrics_json(sample_metrics)
        metric = formatted_data["metrics"][0]
        
        # Verify timestamp is ISO format string
        timestamp_str = metric["timestamp"]
        assert isinstance(timestamp_str, str)
        
        # Should be parseable as ISO datetime
        parsed_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert isinstance(parsed_timestamp, datetime)

    def test_format_metrics_json_metadata_timestamp(self, s3_storage, sample_metrics):
        """Test JSON formatter metadata timestamp."""
        formatted_data = s3_storage.format_metrics_json(sample_metrics)
        metadata = formatted_data["metadata"]
        
        # Verify last_updated is ISO format string
        last_updated_str = metadata["last_updated"]
        assert isinstance(last_updated_str, str)
        
        # Should be parseable as ISO datetime
        parsed_timestamp = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
        assert isinstance(parsed_timestamp, datetime)

    def test_format_metrics_json_error_handling(self, s3_storage):
        """Test JSON formatter error handling with invalid metrics."""
        # Create invalid metrics (missing required attributes)
        invalid_metric = Mock()
        invalid_metric.symbol = "BTC"
        invalid_metric.current_metrics = None  # Invalid
        invalid_metric.momentum_metrics = Mock()
        invalid_metric.timestamp = datetime.now()
        
        with pytest.raises(LunarCrushDataValidationError, match="Failed to format metrics for JSON"):
            s3_storage.format_metrics_json([invalid_metric])

    def test_interface_implementation(self, s3_storage):
        """Test that S3Storage implements IS3Storage interface."""
        assert isinstance(s3_storage, IS3Storage)
        
        # Verify all required methods are implemented
        assert hasattr(s3_storage, 'store_metrics')
        assert hasattr(s3_storage, 'get_current_metrics')
        assert hasattr(s3_storage, 'archive_current_file')
        assert hasattr(s3_storage, 'list_archive_files')
        assert hasattr(s3_storage, 'format_metrics_json')
        
        # Verify methods are callable
        assert callable(getattr(s3_storage, 'store_metrics'))
        assert callable(getattr(s3_storage, 'get_current_metrics'))
        assert callable(getattr(s3_storage, 'archive_current_file'))
        assert callable(getattr(s3_storage, 'list_archive_files'))
        assert callable(getattr(s3_storage, 'format_metrics_json'))

    def test_metadata_in_storage_request(self, s3_storage, sample_metrics, mock_s3_client):
        """Test that metadata is included in storage requests."""
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.copy_object.return_value = {}

        s3_storage.store_metrics(sample_metrics)

        # Verify metadata in put_object call
        call_args = mock_s3_client.put_object.call_args
        metadata = call_args[1]["Metadata"]
        
        assert "symbols_count" in metadata
        assert "last_updated" in metadata
        assert metadata["symbols_count"] == "1"

    def test_content_type_in_storage_request(self, s3_storage, sample_metrics, mock_s3_client):
        """Test that content type is set correctly in storage requests."""
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.copy_object.return_value = {}

        s3_storage.store_metrics(sample_metrics)

        # Verify content type in put_object call
        call_args = mock_s3_client.put_object.call_args
        assert call_args[1]["ContentType"] == "application/json"

    def test_archive_filename_format(self, s3_storage, mock_s3_client):
        """Test archive filename format includes timestamp."""
        mock_s3_client.head_object.return_value = {}  # Current file exists
        mock_s3_client.copy_object.return_value = {}

        with patch('src.adapters.s3_storage.datetime') as mock_datetime:
            mock_now = datetime(2025, 1, 1, 12, 30, 45)
            mock_datetime.now.return_value = mock_now
            mock_datetime.now.side_effect = lambda tz=None: mock_now

            result = s3_storage.archive_current_file()

            expected_filename = "archive/candidates_20250101_123045.json"
            assert result == expected_filename

    def test_archive_files_sorted_by_recency(self, s3_storage, mock_s3_client):
        """Test that archive files are sorted by recency (newest first)."""
        mock_paginator = Mock()
        mock_s3_client.get_paginator.return_value = mock_paginator
        
        # Files in random order
        files = [
            {"Key": "archive/candidates_20250101_120000.json"},
            {"Key": "archive/candidates_20250101_100000.json"},
            {"Key": "archive/candidates_20250101_140000.json"},
            {"Key": "archive/candidates_20250101_130000.json"}
        ]
        
        mock_paginator.paginate.return_value = [{"Contents": files}]

        result = s3_storage.list_archive_files()

        # Should be sorted newest first
        expected_order = [
            "archive/candidates_20250101_140000.json",
            "archive/candidates_20250101_130000.json",
            "archive/candidates_20250101_120000.json",
            "archive/candidates_20250101_100000.json"
        ]
        
        assert result == expected_order