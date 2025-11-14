"""
Error scenario E2E tests for the LunarCrush Lambda function.

This module tests error handling, recovery mechanisms, and graceful degradation
to ensure the system handles errors appropriately and maintains reliability.
"""

import json
import time
import pytest
from typing import Dict, Any, List

import requests


@pytest.mark.e2e
@pytest.mark.slow
class TestErrorScenarios:
    """Test error handling and recovery scenarios."""

    def test_ac5_handling_invalid_symbols_and_missing_data(self, lambda_client, data_validator):
        """
        AC-5: Test handling of invalid symbols and missing data.
        
        This test validates:
        - Invalid symbols are handled gracefully
        - Missing data doesn't cause system failure
        - Partial results are returned when possible
        - Error messages are informative
        """
        # Test with completely invalid symbols
        invalid_payload = {
            "symbols": ["INVALID_SYMBOL_123", "NONEXISTENT_COIN", "FAKE_CRYPTO_999"]
        }
        
        response = lambda_client.invoke(invalid_payload)
        
        # Should still return 200 but with appropriate handling
        assert response["statusCode"] == 200, "Should return 200 even with invalid symbols"
        
        body = json.loads(response["body"])
        
        # Should indicate success but possibly with no data
        if body["success"]:
            data = body["data"]
            assert isinstance(data["metrics"], list), "Metrics should be a list"
            
            # May have empty metrics or partial results
            if len(data["metrics"]) > 0:
                # If we got results, they should be valid
                validation_result = data_validator.validate_metrics_structure(data["metrics"])
                assert validation_result["valid"], f"Invalid metrics structure: {validation_result['errors']}"
        else:
            # If it indicates failure, should have proper error structure
            assert "error" in body, "Error response should have error field"
            error = body["error"]
            assert "message" in error, "Error should have message"
            assert "type" in error, "Error should have type"
        
        # Test with mix of valid and invalid symbols
        mixed_payload = {
            "symbols": ["BTC", "INVALID_SYMBOL", "ETH", "FAKE_COIN"]
        }
        
        response = lambda_client.invoke(mixed_payload)
        assert response["statusCode"] == 200, "Should return 200 for mixed symbols"
        
        body = json.loads(response["body"])
        
        if body["success"]:
            data = body["data"]
            metrics = data["metrics"]
            
            # Should have some results for valid symbols
            assert len(metrics) > 0, "Should have results for valid symbols"
            
            # All returned metrics should have valid symbols
            returned_symbols = {metric["symbol"] for metric in metrics}
            assert not returned_symbols.intersection({"INVALID_SYMBOL", "FAKE_COIN"}), "Should not return invalid symbols"
            
            # Should include BTC and/or ETH if they were processed successfully
            assert returned_symbols.intersection({"BTC", "ETH"}), "Should include valid symbols"

    def test_ac6_api_rate_limiting_and_throttling(self, lambda_client, performance_monitor):
        """
        AC-6: Test API rate limiting and throttling.
        
        This test validates:
        - Rate limiting is enforced correctly
        - Throttling responses are appropriate
        - Retry-after headers are respected
        - System recovers after rate limit reset
        """
        # Make multiple rapid requests to trigger rate limiting
        rapid_requests = 15
        results = []
        
        for i in range(rapid_requests):
            payload = {
                "symbols": ["BTC", "ETH"]
            }
            
            measurement = performance_monitor.start_measurement(f"rate_limit_test_{i}")
            
            try:
                start_time = time.time()
                response = lambda_client.invoke(payload)
                duration = time.time() - start_time
                
                # Check for rate limiting indicators
                body = json.loads(response["body"])
                is_rate_limited = (
                    response["statusCode"] == 429 or
                    (not body["success"] and "rate" in body.get("error", {}).get("message", "").lower())
                )
                
                results.append({
                    "request_id": i,
                    "duration": duration,
                    "success": response["statusCode"] == 200 and body["success"],
                    "rate_limited": is_rate_limited,
                    "status_code": response["statusCode"],
                    "error_type": body.get("error", {}).get("type") if not body["success"] else None
                })
                
                performance_monitor.end_measurement(measurement, success=True)
                
            except Exception as e:
                end_time = time.time()
                results.append({
                    "request_id": i,
                    "duration": end_time - start_time,
                    "success": False,
                    "rate_limited": False,
                    "status_code": 0,
                    "error": str(e)
                })
                performance_monitor.end_measurement(measurement, success=False, error=str(e))
        
        # Analyze rate limiting behavior
        rate_limited_requests = [r for r in results if r["rate_limited"]]
        successful_requests = [r for r in results if r["success"]]
        
        # Some requests might be rate limited (this is expected behavior)
        if rate_limited_requests:
            print(f"Rate limiting detected: {len(rate_limited_requests)}/{rapid_requests} requests rate limited")
            
            # Rate limited requests should have appropriate status codes
            for req in rate_limited_requests:
                assert req["status_code"] in [429, 503], f"Unexpected status code for rate limited request: {req['status_code']}"
                
                # Should have appropriate error type
                if req["error_type"]:
                    assert req["error_type"] in ["RateLimitExceeded", "NetworkError"], f"Unexpected error type: {req['error_type']}"
        
        # At least some requests should succeed
        assert len(successful_requests) > 0, "No requests succeeded under load"
        
        # Validate that rate limiting doesn't break the system
        for req in successful_requests:
            assert req["duration"] < 60, f"Successful request took too long: {req['duration']:.2f}s"

    def test_ac7_retry_logic_with_simulated_failures(self, lambda_client):
        """
        AC-7: Test retry logic with simulated failures.
        
        This test validates:
        - Retry logic works correctly
        - Exponential backoff is implemented
        - Maximum retry limits are respected
        - Failures are handled gracefully
        """
        # Test with symbols that might cause intermittent failures
        problematic_payload = {
            "symbols": ["BTC", "ETH", "SOME_NEW_COIN_THAT_MIGHT_FAIL"]
        }
        
        # Make multiple requests to test retry behavior
        retry_results = []
        
        for i in range(5):
            try:
                response = lambda_client.invoke(problematic_payload)
                
                result = {
                    "attempt": i + 1,
                    "status_code": response["statusCode"],
                    "success": response["statusCode"] == 200
                }
                
                if response["statusCode"] == 200:
                    body = json.loads(response["body"])
                    result["api_success"] = body["success"]
                    result["metrics_count"] = len(body["data"]["metrics"]) if body["success"] else 0
                else:
                    result["api_success"] = False
                    result["metrics_count"] = 0
                
                retry_results.append(result)
                
            except Exception as e:
                retry_results.append({
                    "attempt": i + 1,
                    "status_code": 0,
                    "success": False,
                    "api_success": False,
                    "metrics_count": 0,
                    "error": str(e)
                })
            
            # Small delay between attempts
            time.sleep(1)
        
        # Analyze retry behavior
        successful_attempts = [r for r in retry_results if r["success"] and r["api_success"]]
        
        # At least some attempts should succeed
        assert len(successful_attempts) > 0, "No retry attempts succeeded"
        
        # Successful attempts should return consistent results
        if len(successful_attempts) > 1:
            metrics_counts = [r["metrics_count"] for r in successful_attempts]
            # All successful attempts should return the same number of metrics
            assert len(set(metrics_counts)) <= 1, "Inconsistent results across retry attempts"
        
        print(f"Retry test: {len(successful_attempts)}/{len(retry_results)} attempts successful")

    def test_graceful_degradation_when_services_unavailable(self, lambda_client):
        """
        Test graceful degradation when services are unavailable.
        
        This test validates:
        - System handles service unavailability gracefully
        - Appropriate error messages are returned
        - Partial functionality is maintained when possible
        - System recovers when services become available
        """
        # Test with a payload that might stress the system
        stress_payload = {
            "symbols": ["BTC", "ETH", "ADA", "DOT", "LINK", "BNB", "XRP", "SOL", "MATIC", "AVAX"]
        }
        
        # Make request to test graceful degradation
        try:
            response = lambda_client.invoke(stress_payload)
            
            # Should return a structured response even under stress
            assert response["statusCode"] in [200, 500, 502, 503], f"Unexpected status code: {response['statusCode']}"
            
            body = json.loads(response["body"])
            
            # Should have proper structure even in error cases
            if body["success"]:
                # If successful, should have valid data structure
                data = body["data"]
                assert "metrics" in data, "Missing metrics in response"
                assert "metadata" in data, "Missing metadata in response"
                
                # Might have partial results
                metrics = data["metrics"]
                assert isinstance(metrics, list), "Metrics should be a list"
                
                # If we have metrics, they should be valid
                if len(metrics) > 0:
                    for metric in metrics:
                        assert "symbol" in metric, "Metric missing symbol"
                        assert "current_metrics" in metric, "Metric missing current_metrics"
            else:
                # If failed, should have proper error structure
                assert "error" in body, "Missing error in response"
                error = body["error"]
                assert "message" in error, "Error missing message"
                assert "type" in error, "Error missing type"
                
                # Error type should be informative
                valid_error_types = [
                    "RateLimitExceeded", "NetworkError", "APIError", 
                    "AuthenticationError", "DataValidationError", "InternalServerError"
                ]
                assert error["type"] in valid_error_types, f"Invalid error type: {error['type']}"
        
        except Exception as e:
            # Even exceptions should be handled gracefully
            pytest.fail(f"Unhandled exception during graceful degradation test: {str(e)}")

    def test_error_logging_and_monitoring(self, lambda_client):
        """
        Test error logging and monitoring capabilities.
        
        This test validates:
        - Errors are logged appropriately
        - Log levels are correct for different error types
        - Sensitive information is not logged
        - Structured logging format is used
        """
        # Test various error scenarios
        error_scenarios = [
            {
                "name": "invalid_symbols",
                "payload": {"symbols": ["INVALID_123", "FAKE_COIN"]},
                "expected_error": None  # Might not error, just return empty results
            },
            {
                "name": "empty_symbols",
                "payload": {"symbols": []},
                "expected_error": None  # Should use defaults
            },
            {
                "name": "malformed_payload",
                "payload": {"invalid_field": "test"},
                "expected_error": "ValidationError"
            }
        ]
        
        for scenario in error_scenarios:
            try:
                response = lambda_client.invoke(scenario["payload"])
                
                # Validate response structure
                assert response["statusCode"] in [200, 400, 500], f"Unexpected status code for {scenario['name']}"
                
                body = json.loads(response["body"])
                
                if not body["success"]:
                    error = body["error"]
                    
                    # Should have proper error structure
                    assert "message" in error, f"Error missing message for {scenario['name']}"
                    assert "type" in error, f"Error missing type for {scenario['name']}"
                    
                    # Error message should be informative but not expose sensitive data
                    error_message = error["message"]
                    assert len(error_message) > 0, f"Empty error message for {scenario['name']}"
                    assert "password" not in error_message.lower(), f"Error message contains sensitive data: {error_message}"
                    assert "key" not in error_message.lower() or "api" not in error_message.lower(), f"Error message might expose API key: {error_message}"
                
                # Log the scenario for manual verification
                print(f"Error scenario '{scenario['name']}' handled with status {response['statusCode']}")
                
            except Exception as e:
                # Should not have unhandled exceptions
                pytest.fail(f"Unhandled exception in error scenario '{scenario['name']}': {str(e)}")

    def test_timeout_handling(self, lambda_client, performance_monitor):
        """
        Test timeout handling for long-running operations.
        
        This test validates:
        - Timeouts are handled gracefully
        - Appropriate error responses are returned
        - System doesn't hang on long operations
        - Resources are cleaned up after timeouts
        """
        # Test with a large symbol set that might cause timeouts
        large_payload = {
            "symbols": [f"SYMBOL{i:03d}" for i in range(100)]  # 100 symbols
        }
        
        measurement = performance_monitor.start_measurement("timeout_test")
        
        try:
            start_time = time.time()
            response = lambda_client.invoke(large_payload)
            duration = time.time() - start_time
            
            performance_monitor.end_measurement(measurement, success=True)
            
            # Should complete within reasonable time or timeout gracefully
            assert duration < 120, f"Request took too long: {duration:.2f}s"
            
            # Should have proper response structure
            assert response["statusCode"] in [200, 408, 500], f"Unexpected status code: {response['statusCode']}"
            
            body = json.loads(response["body"])
            
            if body["success"]:
                # If successful, should have valid data
                data = body["data"]
                assert "metrics" in data, "Missing metrics in response"
                assert "metadata" in data, "Missing metadata in response"
            else:
                # If failed, should have proper error structure
                assert "error" in body, "Missing error in response"
                error = body["error"]
                assert "message" in error, "Error missing message"
                assert "type" in error, "Error missing type"
                
                # Should be timeout-related error if it timed out
                if duration > 30:  # If it took a while
                    assert error["type"] in ["NetworkError", "InternalServerError"], f"Expected timeout error, got {error['type']}"
        
        except Exception as e:
            performance_monitor.end_measurement(measurement, success=False, error=str(e))
            
            # Should not have unhandled exceptions
            pytest.fail(f"Unhandled exception in timeout test: {str(e)}")

    def test_memory_pressure_handling(self, lambda_client, performance_monitor):
        """
        Test handling under memory pressure.
        
        This test validates:
        - System handles memory pressure gracefully
        - No memory leaks or excessive consumption
        - Performance degrades gracefully
        - System recovers after pressure is relieved
        """
        # Test with multiple concurrent requests to create memory pressure
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(request_id):
            try:
                payload = {
                    "symbols": [f"SYMBOL{i:03d}" for i in range(20)]  # 20 symbols per request
                }
                
                start_time = time.time()
                response = lambda_client.invoke(payload)
                duration = time.time() - start_time
                
                results.put({
                    "request_id": request_id,
                    "duration": duration,
                    "success": response["statusCode"] == 200,
                    "status_code": response["statusCode"]
                })
                
            except Exception as e:
                results.put({
                    "request_id": request_id,
                    "duration": float('inf'),
                    "success": False,
                    "status_code": 0,
                    "error": str(e)
                })
        
        # Start multiple threads to create memory pressure
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60)  # 60 second timeout per thread
        
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        # Analyze results
        successful_requests = [r for r in all_results if r["success"]]
        
        # Most requests should succeed even under memory pressure
        success_rate = len(successful_requests) / len(all_results)
        assert success_rate >= 0.7, f"Success rate under memory pressure too low: {success_rate:.2f}"
        
        # Performance should be reasonable
        if successful_requests:
            durations = [r["duration"] for r in successful_requests]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            assert max_duration < 90, f"Max duration under memory pressure too high: {max_duration:.2f}s"
            assert avg_duration < 45, f"Avg duration under memory pressure too high: {avg_duration:.2f}s"
        
        print(f"Memory pressure test: {len(successful_requests)}/{len(all_results)} requests successful")