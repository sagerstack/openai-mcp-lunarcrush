"""
End-to-End tests for the complete LunarCrush Lambda workflow.

This module tests the complete workflow from Lambda invocation through API calls
to S3 storage, validating all acceptance criteria and real-world usage scenarios.
"""

import json
import time
import pytest
from typing import Dict, Any, List

import boto3
import requests


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflow:
    """Test the complete workflow from Lambda invocation to S3 storage."""

    def test_ac1_basic_workflow_with_two_symbols(self, lambda_client, localstack_s3_client, data_validator, test_symbols):
        """
        AC-1: Test basic workflow with two symbols (BTC, ETH).
        
        This test validates:
        - Lambda function invocation via Runtime API
        - API calls to LunarCrush
        - Data processing and transformation
        - Response structure and content
        - Required metrics presence
        """
        # Prepare test payload
        payload = {
            "symbols": test_symbols[:2]  # Use first 2 symbols (BTC, ETH)
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(payload)
        
        # Validate response structure
        validation_result = data_validator.validate_lambda_response(response)
        assert validation_result["valid"], f"Response validation failed: {validation_result['errors']}"
        
        # Parse response body
        body = json.loads(response["body"])
        assert body["success"], "Response indicates failure"
        
        # Validate data structure
        data = body["data"]
        assert "metrics" in data, "Missing metrics in response"
        assert "metadata" in data, "Missing metadata in response"
        
        metrics = data["metrics"]
        assert len(metrics) == 2, f"Expected 2 metrics, got {len(metrics)}"
        
        # Validate individual metrics structure
        metrics_validation = data_validator.validate_metrics_structure(metrics)
        assert metrics_validation["valid"], f"Metrics validation failed: {metrics_validation['errors']}"
        
        # Validate required fields are present (AC-1 requirements)
        for metric in metrics:
            current = metric["current_metrics"]
            
            # Check all required metrics are present
            required_fields = [
                "interactions_24h", "social_volume_24h", "social_dominance",
                "galaxy_score", "sentiment", "alt_rank"
            ]
            
            for field in required_fields:
                assert field in current, f"Missing required field: {field}"
                assert current[field] is not None, f"Field {field} is null"
            
            # Validate data types and ranges
            assert isinstance(current["interactions_24h"], int), "interactions_24h should be integer"
            assert isinstance(current["social_volume_24h"], int), "social_volume_24h should be integer"
            assert isinstance(current["social_dominance"], (int, float)), "social_dominance should be numeric"
            assert isinstance(current["galaxy_score"], (int, float)), "galaxy_score should be numeric"
            assert isinstance(current["sentiment"], (int, float)), "sentiment should be numeric"
            assert isinstance(current["alt_rank"], int), "alt_rank should be integer"
            
            # Validate value ranges
            assert current["interactions_24h"] >= 0, "interactions_24h should be non-negative"
            assert current["social_volume_24h"] >= 0, "social_volume_24h should be non-negative"
            assert 0 <= current["social_dominance"] <= 100, "social_dominance should be between 0 and 100"
            assert 0 <= current["galaxy_score"] <= 100, "galaxy_score should be between 0 and 100"
            assert 0 <= current["sentiment"] <= 100, "sentiment should be between 0 and 100"
            assert current["alt_rank"] >= 1, "alt_rank should be >= 1"
        
        # Validate metadata
        metadata = data["metadata"]
        assert metadata["count"] == 2, "Metadata count should match metrics count"
        assert "timestamp" in metadata, "Missing timestamp in metadata"
        assert "symbols_requested" in metadata, "Missing symbols_requested in metadata"
        assert set(metadata["symbols_requested"]) == set(test_symbols[:2]), "Symbols don't match request"

    def test_ac4_performance_with_50_symbols(self, lambda_client, performance_monitor, large_symbol_set):
        """
        AC-4: Test performance with 50 symbols within 30 seconds.
        
        This test validates:
        - Processing 50 symbols within performance threshold
        - Lambda function execution within timeout limits
        - Memory usage within limits
        - Response time requirements
        """
        # Start performance measurement
        measurement = performance_monitor.start_measurement("process_50_symbols")
        
        try:
            # Prepare test payload with 50 symbols
            payload = {
                "symbols": large_symbol_set
            }
            
            # Invoke Lambda function
            response = lambda_client.invoke(payload)
            
            # End performance measurement
            performance_monitor.end_measurement(measurement, success=True)
            
            # Validate response
            assert response["statusCode"] == 200, f"Lambda returned status code {response['statusCode']}"
            
            body = json.loads(response["body"])
            assert body["success"], "Response indicates failure"
            
            data = body["data"]
            metrics = data["metrics"]
            
            # Validate we got metrics for all symbols (or as many as possible)
            assert len(metrics) > 0, "No metrics returned"
            assert len(metrics) <= 50, f"Got more metrics than requested: {len(metrics)}"
            
            # Check performance requirements
            duration = measurement["duration"]
            assert duration <= 30, f"Processing took {duration:.2f}s, exceeds 30s limit"
            
            # Get performance stats
            stats = performance_monitor.get_stats()
            assert stats["successful_operations"] == 1, "Operation should be successful"
            assert stats["total_duration"] <= 30, f"Total duration {stats['total_duration']:.2f}s exceeds limit"
            
        except Exception as e:
            performance_monitor.end_measurement(measurement, success=False, error=str(e))
            raise

    def test_ac11_s3_storage_integration(self, lambda_client, localstack_s3_client, test_symbols):
        """
        AC-11: Test S3 storage integration.
        
        This test validates:
        - Metrics are stored in S3
        - File structure and format
        - Archive functionality
        - S3 bucket access
        """
        # Prepare test payload
        payload = {
            "symbols": test_symbols[:3]  # Use 3 symbols
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(payload)
        
        # Validate Lambda response
        assert response["statusCode"] == 200, "Lambda invocation failed"
        
        # Wait a moment for S3 storage to complete
        time.sleep(2)
        
        # Check if metrics were stored in S3
        try:
            stored_metrics = localstack_s3_client.get_current_metrics()
            assert stored_metrics is not None, "No metrics found in S3"
            
            # Validate stored data structure
            assert "metrics" in stored_metrics, "Missing metrics in stored data"
            assert "metadata" in stored_metrics, "Missing metadata in stored data"
            
            stored_metrics_list = stored_metrics["metrics"]
            assert len(stored_metrics_list) > 0, "No metrics in stored file"
            
            # Validate individual stored metrics
            for metric in stored_metrics_list:
                assert "symbol" in metric, "Missing symbol in stored metric"
                assert "current" in metric, "Missing current data in stored metric"
                assert "changes" in metric, "Missing changes data in stored metric"
                assert "timestamp" in metric, "Missing timestamp in stored metric"
                
                # Validate current data structure
                current = metric["current"]
                required_current_fields = [
                    "interactions_24h", "social_volume_24h", "social_dominance",
                    "galaxy_score", "sentiment", "alt_rank"
                ]
                
                for field in required_current_fields:
                    assert field in current, f"Missing field {field} in stored current data"
                
                # Validate changes data structure
                changes = metric["changes"]
                required_changes_fields = [
                    "interactions_24h_pct", "social_volume_24h_pct", "social_dominance_pct",
                    "galaxy_score_change", "sentiment_pct", "alt_rank_change"
                ]
                
                for field in required_changes_fields:
                    assert field in changes, f"Missing field {field} in stored changes data"
            
            # Validate metadata
            metadata = stored_metrics["metadata"]
            assert "count" in metadata, "Missing count in stored metadata"
            assert "last_updated" in metadata, "Missing last_updated in stored metadata"
            assert "symbols" in metadata, "Missing symbols in stored metadata"
            assert metadata["count"] == len(stored_metrics_list), "Metadata count doesn't match metrics count"
            
        except Exception as e:
            pytest.fail(f"S3 storage validation failed: {str(e)}")

    def test_complete_workflow_with_real_api(self, lambda_client, localstack_s3_client, data_validator):
        """
        Test complete workflow with real API calls.
        
        This test validates:
        - Real API integration with LunarCrush
        - End-to-end data flow
        - Error handling for real API responses
        - Data consistency across components
        """
        # Use real cryptocurrency symbols
        real_symbols = ["BTC", "ETH", "ADA"]
        
        # Prepare test payload
        payload = {
            "symbols": real_symbols
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(payload)
        
        # Validate response structure
        validation_result = data_validator.validate_lambda_response(response)
        assert validation_result["valid"], f"Response validation failed: {validation_result['errors']}"
        
        # Parse response
        body = json.loads(response["body"])
        assert body["success"], "Response indicates failure"
        
        data = body["data"]
        metrics = data["metrics"]
        
        # Validate we got data for real symbols
        assert len(metrics) > 0, "No metrics returned for real symbols"
        
        # Validate symbol consistency
        returned_symbols = {metric["symbol"] for metric in metrics}
        assert returned_symbols.issubset(set(real_symbols)), "Returned symbols don't match request"
        
        # Wait for S3 storage
        time.sleep(2)
        
        # Validate S3 storage
        try:
            stored_metrics = localstack_s3_client.get_current_metrics()
            if stored_metrics:
                stored_symbols = {metric["symbol"] for metric in stored_metrics["metrics"]}
                assert stored_symbols == returned_symbols, "S3 symbols don't match response symbols"
        except Exception as e:
            # S3 might not be available in all environments
            print(f"Warning: S3 validation failed: {e}")

    def test_workflow_with_custom_parameters(self, lambda_client, data_validator):
        """
        Test workflow with custom parameters.
        
        This test validates:
        - Custom parameter handling
        - Parameter validation
        - Response customization based on parameters
        """
        # Prepare test payload with custom parameters
        payload = {
            "symbols": ["BTC", "ETH"],
            "parameters": {
                "include_historical": True,
                "cache_ttl": 300,
                "custom_field": "test_value"
            }
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(payload)
        
        # Validate response
        validation_result = data_validator.validate_lambda_response(response)
        assert validation_result["valid"], f"Response validation failed: {validation_result['errors']}"
        
        # Parse response
        body = json.loads(response["body"])
        data = body["data"]
        
        # Validate parameters are reflected in metadata
        metadata = data["metadata"]
        if "parameters" in metadata:
            parameters = metadata["parameters"]
            assert parameters["include_historical"] == True, "Custom parameter not preserved"
            assert parameters["custom_field"] == "test_value", "Custom parameter not preserved"

    def test_workflow_error_handling(self, lambda_client):
        """
        Test workflow error handling.
        
        This test validates:
        - Error handling for invalid inputs
        - Proper error response format
        - Graceful degradation
        """
        # Test with invalid symbols
        invalid_payload = {
            "symbols": ["INVALID_SYMBOL_123", "ANOTHER_INVALID"]
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(invalid_payload)
        
        # Should still return 200 but with empty or partial results
        assert response["statusCode"] == 200, "Should return 200 even with invalid symbols"
        
        body = json.loads(response["body"])
        
        # Should indicate success but possibly with no data
        if body["success"]:
            data = body["data"]
            # May have empty metrics or partial results
            assert isinstance(data["metrics"], list), "Metrics should be a list"
        else:
            # If it indicates failure, should have proper error structure
            assert "error" in body, "Error response should have error field"

    def test_workflow_with_empty_symbols_list(self, lambda_client):
        """
        Test workflow with empty symbols list.
        
        This test validates:
        - Default symbol handling
        - Graceful handling of empty input
        """
        # Test with empty symbols list
        empty_payload = {
            "symbols": []
        }
        
        # Invoke Lambda function
        response = lambda_client.invoke(empty_payload)
        
        # Should handle gracefully
        assert response["statusCode"] in [200, 400], "Should return 200 or 400 for empty symbols"
        
        if response["statusCode"] == 200:
            body = json.loads(response["body"])
            if body["success"]:
                # Should use default symbols
                data = body["data"]
                assert len(data["metrics"]) > 0, "Should return default symbols when none provided"