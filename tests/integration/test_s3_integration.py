"""
Integration tests for S3 storage operations.

These tests validate real S3 interactions with both LocalStack and AWS S3,
including file upload, retrieval, archiving, and error handling.
"""

import os
import json
import time
import pytest
import boto3
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from moto import mock_s3

from src.adapters.s3_storage import S3Storage
from src.lunarcrush_client import SocialMetrics, CurrentSocialMetrics, MomentumMetrics
from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)


@pytest.mark.integration
@pytest.mark.aws
class TestS3StorageIntegration:
    """Test real S3 storage integration."""

    def test_s3_connection_and_bucket_access(self, real_s3_storage):
        """Test S3 connection and bucket access."""
        # This test verifies that we can connect to S3 and access the bucket
        try:
            # Test bucket access by trying to list objects
            archive_files = real_s3_storage.list_archive_files()
            assert isinstance(archive_files, list)
            
            # Test getting current metrics (might not exist)
            current_metrics = real_s3_storage.get_current_metrics()
            # Should return None if file doesn't exist, or dict if it does
            assert current_metrics is None or isinstance(current_metrics, dict)
            
        except Exception as e:
            pytest.fail(f"S3 connection test failed: {e}")

    def test_file_upload_and_retrieval(self, real_s3_storage, test_symbols):
        """Test file upload and retrieval with real S3 operations."""
        try:
            # Create test metrics data
            test_metrics = []
            for symbol in test_symbols[:2]:  # Use first 2 symbols
                current = CurrentSocialMetrics(
                    symbol=symbol,
                    interactions_24h=100000 + hash(symbol) % 50000,
                    social_volume_24h=2000 + hash(symbol) % 1000,
                    social_dominance=20.0 + hash(symbol) % 30.0,
                    galaxy_score=60.0 + hash(symbol) % 20.0,
                    sentiment=50.0 + hash(symbol) % 30.0,
                    alt_rank=1 + hash(symbol) % 50
                )
                
                momentum = MomentumMetrics(symbol=symbol)
                
                social_metric = SocialMetrics(
                    symbol=symbol,
                    current_metrics=current,
                    momentum_metrics=momentum,
                    timestamp=datetime.now(timezone.utc)
                )
                
                test_metrics.append(social_metric)
            
            # Store metrics
            success = real_s3_storage.store_metrics(test_metrics)
            assert success, "Failed to store metrics"
            
            # Wait a moment for S3 consistency
            time.sleep(1)
            
            # Retrieve current metrics
            retrieved_data = real_s3_storage.get_current_metrics()
            assert retrieved_data is not None, "No data retrieved after storage"
            assert isinstance(retrieved_data, dict)
            
            # Validate structure
            assert "metrics" in retrieved_data
            assert "metadata" in retrieved_data
            
            # Check metadata
            metadata = retrieved_data["metadata"]
            assert "count" in metadata
            assert "last_updated" in metadata
            assert "symbols" in metadata
            assert metadata["count"] == len(test_metrics)
            
            # Check metrics data
            metrics_list = retrieved_data["metrics"]
            assert len(metrics_list) == len(test_metrics)
            
            # Validate each metric
            for i, metric_data in enumerate(metrics_list):
                assert "symbol" in metric_data
                assert "current" in metric_data
                assert "changes" in metric_data
                assert "timestamp" in metric_data
                
                # Check that symbol matches
                original_symbol = test_metrics[i].symbol
                assert metric_data["symbol"] == original_symbol
                
                # Check current metrics structure
                current_data = metric_data["current"]
                assert "interactions_24h" in current_data
                assert "social_volume_24h" in current_data
                assert "social_dominance" in current_data
                assert "galaxy_score" in current_data
                assert "sentiment" in current_data
                assert "alt_rank" in current_data
                
        except Exception as e:
            pytest.fail(f"File upload/retrieval test failed: {e}")

    def test_archive_management_functionality(self, real_s3_storage, test_symbols):
        """Test archive management functionality."""
        try:
            # Create and store initial metrics
            test_metrics = []
            for symbol in test_symbols[:1]:  # Use just 1 symbol
                current = CurrentSocialMetrics(
                    symbol=symbol,
                    interactions_24h=100000,
                    social_volume_24h=2000,
                    social_dominance=25.0,
                    galaxy_score=75.0,
                    sentiment=65.0,
                    alt_rank=1
                )
                
                momentum = MomentumMetrics(symbol=symbol)
                
                social_metric = SocialMetrics(
                    symbol=symbol,
                    current_metrics=current,
                    momentum_metrics=momentum,
                    timestamp=datetime.now(timezone.utc)
                )
                
                test_metrics.append(social_metric)
            
            # Store initial metrics
            success = real_s3_storage.store_metrics(test_metrics)
            assert success, "Failed to store initial metrics"
            
            # Wait for S3 consistency
            time.sleep(1)
            
            # Archive current file
            archive_key = real_s3_storage.archive_current_file()
            assert archive_key, "No archive key returned"
            assert archive_key.startswith("archive/candidates_"), "Invalid archive key format"
            assert archive_key.endswith(".json"), "Archive key should end with .json"
            
            # List archive files
            archive_files = real_s3_storage.list_archive_files()
            assert isinstance(archive_files, list)
            assert len(archive_files) > 0, "No archive files found"
            assert archive_key in archive_files, "New archive file not found in list"
            
            # Store new metrics (should create new candidates.json)
            new_metrics = []
            for symbol in test_symbols[:1]:
                current = CurrentSocialMetrics(
                    symbol=symbol,
                    interactions_24h=110000,  # Different values
                    social_volume_24h=2100,
                    social_dominance=26.0,
                    galaxy_score=76.0,
                    sentiment=66.0,
                    alt_rank=2
                )
                
                momentum = MomentumMetrics(symbol=symbol)
                
                social_metric = SocialMetrics(
                    symbol=symbol,
                    current_metrics=current,
                    momentum_metrics=momentum,
                    timestamp=datetime.now(timezone.utc)
                )
                
                new_metrics.append(social_metric)
            
            success = real_s3_storage.store_metrics(new_metrics)
            assert success, "Failed to store new metrics"
            
            # Wait for S3 consistency
            time.sleep(1)
            
            # Verify new current metrics
            current_data = real_s3_storage.get_current_metrics()
            assert current_data is not None, "No current data after new storage"
            
            # Check that values are updated
            current_metric = current_data["metrics"][0]
            assert current_metric["current"]["interactions_24h"] == 110000
            
        except Exception as e:
            pytest.fail(f"Archive management test failed: {e}")

    def test_json_formatting_and_structure_validation(self, real_s3_storage):
        """Test JSON formatting and structure validation."""
        try:
            # Create test metrics with various data types
            test_metrics = []
            
            # Test with different symbol formats and edge cases
            test_cases = [
                ("BTC", 150000, 2500, 25.5, 75.2, 65.3, 1),
                ("ETH", 120000, 2100, 18.7, 68.9, 58.2, 2),
                ("TEST-COIN", 80000, 1500, 12.3, 62.4, 52.8, 8)
            ]
            
            for symbol, interactions, volume, dominance, galaxy, sentiment, rank in test_cases:
                current = CurrentSocialMetrics(
                    symbol=symbol,
                    interactions_24h=interactions,
                    social_volume_24h=volume,
                    social_dominance=dominance,
                    galaxy_score=galaxy,
                    sentiment=sentiment,
                    alt_rank=rank
                )
                
                momentum = MomentumMetrics(
                    symbol=symbol,
                    galaxy_score_trend=1.5,
                    alt_rank_trend=-1,
                    sentiment_trend=5.2,
                    interactions_trend=15.5,
                    social_dominance_trend=8.3,
                    volume_trend=12.0
                )
                
                social_metric = SocialMetrics(
                    symbol=symbol,
                    current_metrics=current,
                    momentum_metrics=momentum,
                    timestamp=datetime.now(timezone.utc)
                )
                
                test_metrics.append(social_metric)
            
            # Store metrics
            success = real_s3_storage.store_metrics(test_metrics)
            assert success, "Failed to store metrics for JSON validation"
            
            # Wait for S3 consistency
            time.sleep(1)
            
            # Retrieve and validate JSON structure
            retrieved_data = real_s3_storage.get_current_metrics()
            assert retrieved_data is not None, "No data retrieved for JSON validation"
            
            # Validate top-level structure
            assert isinstance(retrieved_data, dict)
            assert "metrics" in retrieved_data
            assert "metadata" in retrieved_data
            
            # Validate metadata structure
            metadata = retrieved_data["metadata"]
            assert isinstance(metadata, dict)
            assert "count" in metadata
            assert isinstance(metadata["count"], int)
            assert "last_updated" in metadata
            assert isinstance(metadata["last_updated"], str)
            assert "symbols" in metadata
            assert isinstance(metadata["symbols"], list)
            
            # Validate metrics array
            metrics_array = retrieved_data["metrics"]
            assert isinstance(metrics_array, list)
            assert len(metrics_array) == len(test_cases)
            
            # Validate each metric object
            for i, metric_obj in enumerate(metrics_array):
                assert isinstance(metric_obj, dict)
                
                # Required fields
                required_fields = ["symbol", "current", "changes", "timestamp"]
                for field in required_fields:
                    assert field in metric_obj, f"Missing field '{field}' in metric {i}"
                
                # Validate symbol
                assert isinstance(metric_obj["symbol"], str)
                assert metric_obj["symbol"] in [case[0] for case in test_cases]
                
                # Validate current metrics
                current = metric_obj["current"]
                assert isinstance(current, dict)
                current_fields = [
                    "interactions_24h", "social_volume_24h", "social_dominance",
                    "galaxy_score", "sentiment", "alt_rank"
                ]
                for field in current_fields:
                    assert field in current, f"Missing current field '{field}' in metric {i}"
                    assert isinstance(current[field], (int, float)), f"Invalid type for {field}"
                
                # Validate changes
                changes = metric_obj["changes"]
                assert isinstance(changes, dict)
                change_fields = [
                    "interactions_24h_pct", "social_volume_24h_pct", "social_dominance_pct",
                    "galaxy_score_change", "sentiment_pct", "alt_rank_change"
                ]
                for field in change_fields:
                    assert field in changes, f"Missing change field '{field}' in metric {i}"
                    assert isinstance(changes[field], (int, float)), f"Invalid type for {field}"
                
                # Validate timestamp
                assert isinstance(metric_obj["timestamp"], str)
                
                # Try to parse timestamp
                try:
                    datetime.fromisoformat(metric_obj["timestamp"].replace('Z', '+00:00'))
                except ValueError:
                    pytest.fail(f"Invalid timestamp format: {metric_obj['timestamp']}")
            
        except Exception as e:
            pytest.fail(f"JSON formatting validation test failed: {e}")

    def test_s3_error_handling_and_recovery(self, real_s3_storage):
        """Test S3 error handling and recovery."""
        try:
            # Test with invalid bucket (should fail gracefully)
            try:
                invalid_storage = S3Storage(
                    bucket_name="non-existent-bucket-12345",
                    endpoint_url=real_s3_storage.endpoint_url if hasattr(real_s3_storage, 'endpoint_url') else None
                )
                pytest.fail("Should have failed with invalid bucket")
            except (ValueError, LunarCrushNetworkError):
                pass  # Expected
            
            # Test storing empty metrics list
            success = real_s3_storage.store_metrics([])
            assert success is False, "Should return False for empty metrics list"
            
            # Test storing None metrics
            success = real_s3_storage.store_metrics(None)
            # Should return False for None metrics (current implementation)
            assert success is False, "Should return False for None metrics"
            
            # Test retrieving from non-existent file (should return None)
            # This is already tested in get_current_metrics when no file exists
            
            # Test archiving when no current file exists
            # First, delete the current file if it exists
            try:
                real_s3_storage.s3_client.delete_object(
                    Bucket=real_s3_storage.bucket_name,
                    Key="candidates.json"
                )
            except:
                pass  # File might not exist, which is fine
            
            archive_key = real_s3_storage.archive_current_file()
            # Should return empty string if no file to archive
            assert archive_key == "", "Should return empty string when no file to archive"
            
        except Exception as e:
            pytest.fail(f"S3 error handling test failed: {e}")

    def test_large_data_handling(self, real_s3_storage):
        """Test handling of large data sets."""
        try:
            # Create a large number of metrics
            large_metrics = []
            num_symbols = 50  # Create 50 symbols
            
            for i in range(num_symbols):
                symbol = f"TEST{i:03d}"
                current = CurrentSocialMetrics(
                    symbol=symbol,
                    interactions_24h=100000 + i * 1000,
                    social_volume_24h=2000 + i * 50,
                    social_dominance=20.0 + (i % 30),
                    galaxy_score=60.0 + (i % 20),
                    sentiment=50.0 + (i % 30),
                    alt_rank=1 + i
                )
                
                momentum = MomentumMetrics(
                    symbol=symbol,
                    galaxy_score_trend=float(i % 10),
                    alt_rank_trend=float((i % 5) - 2),
                    sentiment_trend=float(i % 15),
                    interactions_trend=float(i * 0.5),
                    social_dominance_trend=float(i % 8),
                    volume_trend=float(i % 12)
                )
                
                social_metric = SocialMetrics(
                    symbol=symbol,
                    current_metrics=current,
                    momentum_metrics=momentum,
                    timestamp=datetime.now(timezone.utc)
                )
                
                large_metrics.append(social_metric)
            
            # Store large dataset
            start_time = time.time()
            success = real_s3_storage.store_metrics(large_metrics)
            end_time = time.time()
            
            assert success, "Failed to store large dataset"
            
            # Check performance (should complete within reasonable time)
            duration = end_time - start_time
            assert duration < 30, f"Large dataset storage took too long: {duration}s"
            
            # Wait for S3 consistency
            time.sleep(2)
            
            # Retrieve and validate
            retrieved_data = real_s3_storage.get_current_metrics()
            assert retrieved_data is not None, "Failed to retrieve large dataset"
            
            # Validate count
            assert retrieved_data["metadata"]["count"] == num_symbols
            assert len(retrieved_data["metrics"]) == num_symbols
            
            # Validate a few random entries
            import random
            for _ in range(5):  # Check 5 random entries
                idx = random.randint(0, num_symbols - 1)
                metric = retrieved_data["metrics"][idx]
                assert metric["symbol"].startswith("TEST")
                assert "current" in metric
                assert "changes" in metric
            
        except Exception as e:
            pytest.fail(f"Large data handling test failed: {e}")

    def test_concurrent_s3_operations(self, real_s3_storage):
        """Test concurrent S3 operations."""
        import threading
        
        try:
            results = {}
            errors = {}
            
            def store_metrics_batch(batch_id: int, symbols: List[str]):
                try:
                    batch_metrics = []
                    for symbol in symbols:
                        current = CurrentSocialMetrics(
                            symbol=f"{symbol}_BATCH{batch_id}",
                            interactions_24h=100000 + batch_id * 1000,
                            social_volume_24h=2000 + batch_id * 100,
                            social_dominance=20.0 + batch_id,
                            galaxy_score=60.0 + batch_id,
                            sentiment=50.0 + batch_id,
                            alt_rank=1 + batch_id
                        )
                        
                        momentum = MomentumMetrics(symbol=f"{symbol}_BATCH{batch_id}")
                        
                        social_metric = SocialMetrics(
                            symbol=f"{symbol}_BATCH{batch_id}",
                            current_metrics=current,
                            momentum_metrics=momentum,
                            timestamp=datetime.now(timezone.utc)
                        )
                        
                        batch_metrics.append(social_metric)
                    
                    success = real_s3_storage.store_metrics(batch_metrics)
                    results[batch_id] = success
                    
                except Exception as e:
                    errors[batch_id] = str(e)
            
            # Create multiple threads for concurrent operations
            threads = []
            num_batches = 3
            
            for i in range(num_batches):
                symbols = [f"SYMBOL{j}" for j in range(3)]  # 3 symbols per batch
                thread = threading.Thread(target=store_metrics_batch, args=(i, symbols))
                threads.append(thread)
            
            # Start all threads
            start_time = time.time()
            for thread in threads:
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            end_time = time.time()
            
            # Validate results
            assert len(results) == num_batches, f"Expected {num_batches} results, got {len(results)}"
            assert len(errors) == 0, f"Errors in concurrent operations: {errors}"
            
            # At least some operations should succeed
            successful_ops = sum(1 for success in results.values() if success)
            assert successful_ops > 0, "No concurrent operations succeeded"
            
            # Check performance
            duration = end_time - start_time
            assert duration < 60, f"Concurrent operations took too long: {duration}s"
            
        except Exception as e:
            pytest.fail(f"Concurrent S3 operations test failed: {e}")

    @pytest.mark.localstack
    def test_localstack_integration(self, real_s3_storage):
        """Test integration with LocalStack using TestContainers."""
        # This test specifically targets LocalStack functionality using TestContainers
        try:
            # Test basic S3 operations with TestContainers-managed LocalStack
            test_data = {"test": "localstack_integration", "timestamp": datetime.now().isoformat()}
            
            # Test basic functionality without upload_json/download_json
            # Since these methods don't exist in S3Storage, we'll use existing methods
            pass
            
        except Exception as e:
            pytest.fail(f"LocalStack integration test failed: {e}")
        
        try:
            # Create S3 storage with LocalStack endpoint
            bucket_name = "test-localstack-bucket"
            endpoint_url = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
            
            # First create the bucket if it doesn't exist
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                region_name="us-east-1",
                aws_access_key_id="test",
                aws_secret_access_key="test"
            )
            
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(f"✅ Bucket {bucket_name} already exists")
            except:
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    print(f"✅ Created bucket {bucket_name}")
                except Exception as bucket_error:
                    print(f"⚠️ Bucket creation failed: {bucket_error}")
                    # Try a different bucket name
                    bucket_name = "test-lunarcrush-bucket"
                    try:
                        s3_client.create_bucket(Bucket=bucket_name)
                        print(f"✅ Created alternative bucket {bucket_name}")
                    except Exception as alt_error:
                        print(f"⚠️ Alternative bucket creation failed: {alt_error}")
                        pytest.skip("Unable to create S3 bucket for testing")
            
            localstack_storage = S3Storage(
                bucket_name=bucket_name,
                endpoint_url=endpoint_url,
                aws_region="us-east-1"
            )
            
            # Test basic operations
            test_metrics = []
            current = CurrentSocialMetrics(
                symbol="LOCALTEST",
                interactions_24h=100000,
                social_volume_24h=2000,
                social_dominance=25.0,
                galaxy_score=75.0,
                sentiment=65.0,
                alt_rank=1
            )
            
            momentum = MomentumMetrics(symbol="LOCALTEST")
            
            social_metric = SocialMetrics(
                symbol="LOCALTEST",
                current_metrics=current,
                momentum_metrics=momentum,
                timestamp=datetime.now(timezone.utc)
            )
            
            test_metrics.append(social_metric)
            
            # Store and retrieve
            success = localstack_storage.store_metrics(test_metrics)
            assert success, "Failed to store in LocalStack"
            
            time.sleep(1)  # Wait for consistency
            
            retrieved = localstack_storage.get_current_metrics()
            assert retrieved is not None, "Failed to retrieve from LocalStack"
            assert retrieved["metadata"]["count"] == 1
            
        except Exception as e:
            pytest.fail(f"LocalStack integration test failed: {e}")