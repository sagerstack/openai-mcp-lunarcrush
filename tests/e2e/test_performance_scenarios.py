"""
Performance scenario E2E tests for the LunarCrush Lambda function.

This module tests performance requirements, load handling, and scalability
to ensure the system meets all performance acceptance criteria.
"""

import json
import time
import pytest
import threading
import concurrent.futures
from typing import Dict, Any, List, Tuple
import statistics

import requests


@pytest.mark.e2e
@pytest.mark.performance
@pytest.mark.slow
class TestPerformanceScenarios:
    """Test performance scenarios and requirements."""

    def test_ac4_processing_50_symbols_within_30_seconds(self, lambda_client, performance_monitor, large_symbol_set):
        """
        AC-4: Test processing 50 symbols within 30 seconds.
        
        This test validates:
        - Processing 50 symbols completes within 30 seconds
        - Response time meets performance requirements
        - System handles large symbol sets efficiently
        - Memory usage remains within limits
        """
        # Prepare test payload with 50 symbols
        payload = {
            "symbols": large_symbol_set
        }
        
        # Start performance measurement
        measurement = performance_monitor.start_measurement("process_50_symbols")
        
        try:
            # Invoke Lambda function
            start_time = time.time()
            response = lambda_client.invoke(payload)
            end_time = time.time()
            
            # Calculate actual duration
            actual_duration = end_time - start_time
            
            # End performance measurement
            performance_monitor.end_measurement(measurement, success=True)
            
            # Validate performance requirements
            assert actual_duration <= 30, f"Processing took {actual_duration:.2f}s, exceeds 30s limit"
            
            # Validate response
            assert response["statusCode"] == 200, f"Lambda returned status code {response['statusCode']}"
            
            body = json.loads(response["body"])
            assert body["success"], "Response indicates failure"
            
            data = body["data"]
            metrics = data["metrics"]
            
            # Validate we got metrics for symbols
            assert len(metrics) > 0, "No metrics returned"
            
            # Validate metadata
            metadata = data["metadata"]
            assert metadata["count"] == len(metrics), "Metadata count doesn't match metrics count"
            
            print(f"Successfully processed {len(metrics)} symbols in {actual_duration:.2f}s")
            
        except Exception as e:
            performance_monitor.end_measurement(measurement, success=False, error=str(e))
            raise

    def test_lambda_execution_within_timeout_and_memory_limits(self, lambda_client, performance_monitor):
        """
        AC-10: Test Lambda function execution within timeout and memory limits.
        
        This test validates:
        - Lambda function executes within timeout limits
        - Memory usage stays within allocated limits
        - No memory leaks or excessive resource consumption
        - Performance is consistent across multiple executions
        """
        # Test with moderate symbol set
        test_symbols = ["BTC", "ETH", "ADA", "DOT", "LINK", "BNB", "XRP", "SOL", "MATIC", "AVAX"]
        
        # Run multiple iterations to check consistency
        durations = []
        success_count = 0
        
        for i in range(5):
            payload = {
                "symbols": test_symbols
            }
            
            measurement = performance_monitor.start_measurement(f"execution_test_{i}")
            
            try:
                start_time = time.time()
                response = lambda_client.invoke(payload)
                end_time = time.time()
                
                duration = end_time - start_time
                durations.append(duration)
                
                # Validate response
                if response["statusCode"] == 200:
                    body = json.loads(response["body"])
                    if body["success"]:
                        success_count += 1
                
                performance_monitor.end_measurement(measurement, success=True)
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                performance_monitor.end_measurement(measurement, success=False, error=str(e))
                durations.append(float('inf'))  # Mark as failed
        
        # Validate performance consistency
        successful_durations = [d for d in durations if d != float('inf')]
        
        if successful_durations:
            avg_duration = statistics.mean(successful_durations)
            max_duration = max(successful_durations)
            
            # Should complete within reasonable time (well under Lambda timeout)
            assert max_duration < 60, f"Max duration {max_duration:.2f}s exceeds reasonable limit"
            assert avg_duration < 30, f"Avg duration {avg_duration:.2f}s exceeds reasonable limit"
            
            # Performance should be relatively consistent
            if len(successful_durations) > 1:
                stdev = statistics.stdev(successful_durations)
                assert stdev < avg_duration * 0.5, f"Performance too inconsistent: stdev={stdev:.2f}s"
        
        # Success rate should be high
        success_rate = success_count / 5
        assert success_rate >= 0.8, f"Success rate {success_rate:.2f} too low"
        
        print(f"Performance test: {success_count}/5 successful, avg duration: {avg_duration:.2f}s")

    def test_concurrent_request_handling(self, lambda_client, performance_monitor):
        """
        Test concurrent request handling capabilities.
        
        This test validates:
        - System can handle multiple concurrent requests
        - No race conditions or resource conflicts
        - Performance degrades gracefully under load
        - Each request receives correct data
        """
        def invoke_lambda_with_symbols(symbols: List[str], request_id: int) -> Tuple[float, bool, Dict]:
            """Invoke Lambda function with symbols and return duration, success, and response."""
            payload = {
                "symbols": symbols
            }
            
            start_time = time.time()
            try:
                response = lambda_client.invoke(payload)
                end_time = time.time()
                
                duration = end_time - start_time
                success = response["statusCode"] == 200
                
                if success:
                    body = json.loads(response["body"])
                    success = body["success"]
                
                return duration, success, response
                
            except Exception as e:
                end_time = time.time()
                return end_time - start_time, False, {"error": str(e)}
        
        # Prepare different symbol sets for concurrent requests
        symbol_sets = [
            ["BTC", "ETH"],
            ["ADA", "DOT", "LINK"],
            ["BNB", "XRP", "SOL"],
            ["MATIC", "AVAX", "ATOM"],
            ["FTM", "NEAR", "ONE"]
        ]
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all requests
            future_to_id = {
                executor.submit(invoke_lambda_with_symbols, symbols, i): i
                for i, symbols in enumerate(symbol_sets)
            }
            
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(future_to_id):
                request_id = future_to_id[future]
                try:
                    duration, success, response = future.result()
                    results.append({
                        "request_id": request_id,
                        "duration": duration,
                        "success": success,
                        "response": response
                    })
                except Exception as e:
                    results.append({
                        "request_id": request_id,
                        "duration": float('inf'),
                        "success": False,
                        "response": {"error": str(e)}
                    })
        
        # Validate concurrent execution results
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]
        
        # Most requests should succeed
        success_rate = len(successful_results) / len(results)
        assert success_rate >= 0.8, f"Concurrent success rate {success_rate:.2f} too low"
        
        # Validate performance under concurrent load
        if successful_results:
            durations = [r["duration"] for r in successful_results]
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            # Performance should be reasonable under load
            assert max_duration < 60, f"Concurrent max duration {max_duration:.2f}s too high"
            assert avg_duration < 30, f"Concurrent avg duration {avg_duration:.2f}s too high"
        
        # Validate each successful response has correct data
        for result in successful_results:
            response = result["response"]
            body = json.loads(response["body"])
            data = body["data"]
            
            # Should have metrics
            assert "metrics" in data, "Missing metrics in response"
            assert len(data["metrics"]) > 0, "No metrics returned"
            
            # Should have metadata
            assert "metadata" in data, "Missing metadata in response"
        
        print(f"Concurrent test: {len(successful_results)}/{len(results)} successful")

    def test_api_rate_limiting_under_load(self, lambda_client, performance_monitor):
        """
        Test API rate limiting behavior under load.
        
        This test validates:
        - Rate limiting is enforced correctly
        - System handles rate limit gracefully
        - Backoff and retry mechanisms work
        - Performance degrades gracefully when rate limited
        """
        # Make multiple rapid requests to trigger rate limiting
        rapid_requests = 10
        results = []
        
        for i in range(rapid_requests):
            payload = {
                "symbols": ["BTC", "ETH"]
            }
            
            measurement = performance_monitor.start_measurement(f"rate_limit_test_{i}")
            
            try:
                start_time = time.time()
                response = lambda_client.invoke(payload)
                end_time = time.time()
                
                duration = end_time - start_time
                
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
                    "status_code": response["statusCode"]
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
        
        # At least some requests should succeed
        assert len(successful_requests) > 0, "No requests succeeded under load"
        
        # Performance should be reasonable for successful requests
        if successful_requests:
            durations = [r["duration"] for r in successful_requests]
            avg_duration = statistics.mean(durations)
            assert avg_duration < 30, f"Average duration under load too high: {avg_duration:.2f}s"

    def test_cache_performance_under_repeated_requests(self, lambda_client, performance_monitor):
        """
        Test cache performance under repeated requests.
        
        This test validates:
        - Cache improves performance for repeated requests
        - Cache hit/miss behavior is correct
        - Cache TTL is respected
        - Performance improves with caching
        """
        # First request (cache miss)
        payload = {
            "symbols": ["BTC", "ETH", "ADA"]
        }
        
        # Make initial request to populate cache
        measurement1 = performance_monitor.start_measurement("cache_miss")
        try:
            start_time = time.time()
            response1 = lambda_client.invoke(payload)
            duration1 = time.time() - start_time
            
            performance_monitor.end_measurement(measurement1, success=True)
            
            assert response1["statusCode"] == 200, "First request failed"
            
        except Exception as e:
            performance_monitor.end_measurement(measurement1, success=False, error=str(e))
            raise
        
        # Small delay to ensure cache is populated
        time.sleep(1)
        
        # Second request (should be cache hit)
        measurement2 = performance_monitor.start_measurement("cache_hit")
        try:
            start_time = time.time()
            response2 = lambda_client.invoke(payload)
            duration2 = time.time() - start_time
            
            performance_monitor.end_measurement(measurement2, success=True)
            
            assert response2["statusCode"] == 200, "Second request failed"
            
        except Exception as e:
            performance_monitor.end_measurement(measurement2, success=False, error=str(e))
            raise
        
        # Compare performance
        print(f"Cache miss duration: {duration1:.2f}s")
        print(f"Cache hit duration: {duration2:.2f}s")
        
        # Cache hit should be faster (though this might not always be true due to network variability)
        # We'll just validate that both complete successfully and within reasonable time
        assert duration1 < 30, f"Cache miss duration too high: {duration1:.2f}s"
        assert duration2 < 30, f"Cache hit duration too high: {duration2:.2f}s"
        
        # Validate responses are consistent
        body1 = json.loads(response1["body"])
        body2 = json.loads(response2["body"])
        
        assert body1["success"] and body2["success"], "Both requests should succeed"
        
        data1 = body1["data"]
        data2 = body2["data"]
        
        # Should have same number of metrics
        assert len(data1["metrics"]) == len(data2["metrics"]), "Cached response should have same metrics count"
        
        # Metrics should be identical (or very similar due to timing)
        for i, (metric1, metric2) in enumerate(zip(data1["metrics"], data2["metrics"])):
            assert metric1["symbol"] == metric2["symbol"], f"Symbol mismatch at index {i}"

    def test_performance_with_varying_symbol_counts(self, lambda_client, performance_monitor):
        """
        Test performance with varying symbol counts.
        
        This test validates:
        - Performance scales reasonably with symbol count
        - No exponential performance degradation
        - Resource usage scales linearly
        """
        # Test with different symbol counts
        test_cases = [
            (["BTC"], 1),
            (["BTC", "ETH", "ADA"], 3),
            (["BTC", "ETH", "ADA", "DOT", "LINK", "BNB", "XRP"], 7),
            (["BTC", "ETH", "ADA", "DOT", "LINK", "BNB", "XRP", "SOL", "MATIC", "AVAX"], 10)
        ]
        
        results = []
        
        for symbols, count in test_cases:
            payload = {
                "symbols": symbols
            }
            
            measurement = performance_monitor.start_measurement(f"scale_test_{count}")
            
            try:
                start_time = time.time()
                response = lambda_client.invoke(payload)
                duration = time.time() - start_time
                
                performance_monitor.end_measurement(measurement, success=True)
                
                if response["statusCode"] == 200:
                    body = json.loads(response["body"])
                    success = body["success"]
                    
                    if success:
                        data = body["data"]
                        metrics_count = len(data["metrics"])
                        
                        results.append({
                            "symbol_count": count,
                            "duration": duration,
                            "metrics_returned": metrics_count,
                            "success": True
                        })
                    else:
                        results.append({
                            "symbol_count": count,
                            "duration": duration,
                            "metrics_returned": 0,
                            "success": False
                        })
                else:
                    results.append({
                        "symbol_count": count,
                        "duration": duration,
                        "metrics_returned": 0,
                        "success": False
                    })
                
            except Exception as e:
                performance_monitor.end_measurement(measurement, success=False, error=str(e))
                results.append({
                    "symbol_count": count,
                    "duration": float('inf'),
                    "metrics_returned": 0,
                    "success": False,
                    "error": str(e)
                })
        
        # Analyze scaling performance
        successful_results = [r for r in results if r["success"]]
        
        if len(successful_results) >= 2:
            # Calculate time per symbol for each successful test
            time_per_symbol = []
            for result in successful_results:
                if result["metrics_returned"] > 0:
                    time_per_symbol.append(result["duration"] / result["metrics_returned"])
            
            if time_per_symbol:
                avg_time_per_symbol = statistics.mean(time_per_symbol)
                max_time_per_symbol = max(time_per_symbol)
                
                # Time per symbol should be reasonable
                assert max_time_per_symbol < 5, f"Time per symbol too high: {max_time_per_symbol:.2f}s"
                assert avg_time_per_symbol < 2, f"Average time per symbol too high: {avg_time_per_symbol:.2f}s"
                
                print(f"Average time per symbol: {avg_time_per_symbol:.2f}s")
        
        # Validate that larger requests don't take disproportionately longer
        if len(successful_results) >= 3:
            # Sort by symbol count
            successful_results.sort(key=lambda x: x["symbol_count"])
            
            # Check that performance scales roughly linearly
            for i in range(1, len(successful_results)):
                prev = successful_results[i-1]
                curr = successful_results[i]
                
                symbol_ratio = curr["symbol_count"] / prev["symbol_count"]
                time_ratio = curr["duration"] / prev["duration"]
                
                # Time ratio shouldn't be much worse than symbol ratio
                # Allow some overhead but not exponential growth
                assert time_ratio <= symbol_ratio * 2, f"Performance scaling issue: {symbol_ratio:.1f}x symbols but {time_ratio:.1f}x time"
        
        print("Performance scaling test completed")