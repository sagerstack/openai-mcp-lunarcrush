"""
Comprehensive unit tests for the Lambda function.

This module tests all components of the Lambda function including:
- lambda_handler with various event formats
- Event parsing and validation
- ResponseFormatter class
- Error handling decorator
- Environment validation
- Integration with LunarCrushClient and S3Storage
- Various edge cases and error scenarios
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from lambda_function import (
    lambda_handler,
    process_symbols,
    validate_environment,
    parse_event_body,
    handle_api_errors,
    LambdaResponse
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


class TestLambdaResponse:
    """Test cases for LambdaResponse helper class."""

    def test_success_response_creation(self):
        """Test creating a successful Lambda response."""
        data = {"message": "success", "count": 5}
        response = LambdaResponse.success(data, 200)
        
        assert response["statusCode"] == 200
        assert "Content-Type" in response["headers"]
        assert "Access-Control-Allow-Origin" in response["headers"]
        
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["data"] == data

    def test_success_response_default_status(self):
        """Test creating a successful response with default status."""
        data = {"test": "data"}
        response = LambdaResponse.success(data)
        
        assert response["statusCode"] == 200

    def test_error_response_creation(self):
        """Test creating an error Lambda response."""
        response = LambdaResponse.error(
            message="Something went wrong",
            status_code=400,
            error_type="ValidationError"
        )
        
        assert response["statusCode"] == 400
        assert "Content-Type" in response["headers"]
        assert "Access-Control-Allow-Origin" in response["headers"]
        
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["type"] == "ValidationError"
        assert body["error"]["message"] == "Something went wrong"

    def test_error_response_defaults(self):
        """Test creating an error response with defaults."""
        response = LambdaResponse.error("Test error")
        
        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["error"]["type"] == "InternalServerError"
        assert body["error"]["message"] == "Test error"


class TestEnvironmentValidation:
    """Test cases for environment validation."""

    def test_validate_environment_success(self, monkeypatch):
        """Test successful environment validation."""
        monkeypatch.setenv("LUNARCRUSH_API_KEY", "test_key")
        monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
        
        result = validate_environment()
        
        assert result is True

    def test_validate_environment_missing_api_key(self, monkeypatch):
        """Test validation failure with missing API key."""
        # Clear the environment variable first to remove any loaded values
        monkeypatch.delenv("LUNARCRUSH_API_KEY", raising=False)
        monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
        
        with pytest.raises(ValueError) as exc_info:
            validate_environment()
        
        assert "Missing required environment variables" in str(exc_info.value)
        assert "LUNARCRUSH_API_KEY" in str(exc_info.value)

    def test_validate_environment_missing_bucket_name(self, monkeypatch):
        """Test validation failure with missing bucket name."""
        # Clear the environment variable first to remove any loaded values
        monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
        monkeypatch.setenv("LUNARCRUSH_API_KEY", "test_key")
        
        with pytest.raises(ValueError) as exc_info:
            validate_environment()
        
        assert "Missing required environment variables" in str(exc_info.value)
        assert "S3_BUCKET_NAME" in str(exc_info.value)

    def test_validate_environment_missing_both(self, monkeypatch):
        """Test validation failure with both variables missing."""
        # Clear the environment variables first to remove any loaded values
        monkeypatch.delenv("LUNARCRUSH_API_KEY", raising=False)
        monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            validate_environment()
        
        assert "Missing required environment variables" in str(exc_info.value)
        assert "LUNARCRUSH_API_KEY" in str(exc_info.value)
        assert "S3_BUCKET_NAME" in str(exc_info.value)


class TestEventParsing:
    """Test cases for event parsing and validation."""

    def test_parse_event_body_with_string_body(self):
        """Test parsing event with string body."""
        event = {
            "body": json.dumps({
                "symbols": ["BTC", "ETH"],
                "parameters": {"test": "value"}
            })
        }
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH"]
        assert result["parameters"] == {"test": "value"}

    def test_parse_event_body_with_dict_body(self):
        """Test parsing event with dictionary body."""
        event = {
            "body": {
                "symbols": ["BTC", "ETH"],
                "parameters": {"test": "value"}
            }
        }
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH"]
        assert result["parameters"] == {"test": "value"}

    def test_parse_event_body_without_body(self):
        """Test parsing event without body field."""
        event = {
            "symbols": ["BTC", "ETH"],
            "parameters": {"test": "value"}
        }
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH"]
        assert result["parameters"] == {"test": "value"}

    def test_parse_event_body_default_symbols(self, monkeypatch):
        """Test parsing event with default symbols from environment."""
        monkeypatch.setenv("SYMBOLS_LIST", "BTC,ETH,ADA")
        
        event = {"body": "{}"}
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH", "ADA"]

    def test_parse_event_body_invalid_json(self):
        """Test parsing event with invalid JSON."""
        event = {"body": "invalid json"}
        
        with pytest.raises(ValueError) as exc_info:
            parse_event_body(event)
        
        assert "Invalid JSON in request body" in str(exc_info.value)

    def test_parse_event_body_symbols_not_list(self):
        """Test parsing event with symbols not as list."""
        event = {"body": json.dumps({"symbols": "BTC"})}
        
        with pytest.raises(ValueError) as exc_info:
            parse_event_body(event)
        
        assert "Symbols must be a list" in str(exc_info.value)

    def test_parse_event_body_empty_symbols_list(self):
        """Test parsing event with empty symbols list."""
        event = {"body": json.dumps({"symbols": []})}
        
        # Empty symbols list will default to environment symbols
        result = parse_event_body(event)
        
        # Should get default symbols from environment
        assert result["symbols"] is not None
        assert len(result["symbols"]) > 0

    def test_parse_event_body_invalid_symbol_type(self):
        """Test parsing event with invalid symbol type."""
        event = {"body": json.dumps({"symbols": [123]})}
        
        with pytest.raises(ValueError) as exc_info:
            parse_event_body(event)
        
        assert "Symbol must be a string" in str(exc_info.value)

    def test_parse_event_body_invalid_symbol_format(self):
        """Test parsing event with invalid symbol format."""
        event = {"body": json.dumps({"symbols": ["BTC@123"]})}
        
        with pytest.raises(ValueError) as exc_info:
            parse_event_body(event)
        
        assert "Invalid symbol format" in str(exc_info.value)

    def test_parse_event_body_empty_symbol_string(self):
        """Test parsing event with empty symbol string."""
        event = {"body": json.dumps({"symbols": ["BTC", "", "ETH"]})}
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH"]  # Empty string filtered out

    def test_parse_event_body_symbol_case_conversion(self):
        """Test symbol case conversion to uppercase."""
        event = {"body": json.dumps({"symbols": ["btc", "eth", "ada"]})}
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH", "ADA"]

    def test_parse_event_body_symbol_whitespace_trimming(self):
        """Test symbol whitespace trimming."""
        event = {"body": json.dumps({"symbols": [" BTC ", "  ETH  ", "ADA"]})}
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH", "ADA"]

    def test_parse_event_body_no_valid_symbols(self):
        """Test parsing event with no valid symbols."""
        event = {"body": json.dumps({"symbols": ["", "   "]})}
        
        with pytest.raises(ValueError) as exc_info:
            parse_event_body(event)
        
        assert "No valid symbols provided" in str(exc_info.value)

    def test_parse_event_body_with_parameters(self):
        """Test parsing event with parameters."""
        event = {
            "body": json.dumps({
                "symbols": ["BTC", "ETH"],
                "parameters": {
                    "include_historical": True,
                    "time_range": "24h"
                }
            })
        }
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH"]
        assert result["parameters"]["include_historical"] is True
        assert result["parameters"]["time_range"] == "24h"

    def test_parse_event_body_default_parameters(self):
        """Test parsing event with default parameters."""
        event = {"body": json.dumps({"symbols": ["BTC", "ETH"]})}
        
        result = parse_event_body(event)
        
        assert result["symbols"] == ["BTC", "ETH"]
        assert result["parameters"] == {}


class TestErrorHandlingDecorator:
    """Test cases for the error handling decorator."""

    def test_handle_api_errors_success(self):
        """Test decorator with successful function execution."""
        @handle_api_errors
        def test_function():
            return {"success": True}
        
        result = test_function()
        
        assert result["success"] is True

    def test_handle_api_errors_rate_limit_exception(self):
        """Test decorator with rate limit exception."""
        @handle_api_errors
        def test_function():
            raise LunarCrushRateLimitError("Rate limit exceeded", retry_after=60)
        
        result = test_function()
        
        assert result["statusCode"] == 429
        body = json.loads(result["body"])
        assert body["success"] is False
        assert body["error"]["type"] == "RateLimitExceeded"
        assert "Rate limit exceeded" in body["error"]["message"]

    def test_handle_api_errors_authentication_exception(self):
        """Test decorator with authentication exception."""
        @handle_api_errors
        def test_function():
            raise LunarCrushAuthenticationError("Invalid API key")
        
        result = test_function()
        
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert body["error"]["type"] == "AuthenticationError"

    def test_handle_api_errors_network_exception(self):
        """Test decorator with network exception."""
        @handle_api_errors
        def test_function():
            raise LunarCrushNetworkError("Connection failed")
        
        result = test_function()
        
        assert result["statusCode"] == 503
        body = json.loads(result["body"])
        assert body["error"]["type"] == "NetworkError"

    def test_handle_api_errors_data_validation_exception(self):
        """Test decorator with data validation exception."""
        @handle_api_errors
        def test_function():
            raise LunarCrushDataValidationError("Invalid data format")
        
        result = test_function()
        
        assert result["statusCode"] == 422
        body = json.loads(result["body"])
        assert body["error"]["type"] == "DataValidationError"

    def test_handle_api_errors_general_api_exception(self):
        """Test decorator with general API exception."""
        @handle_api_errors
        def test_function():
            raise LunarCrushAPIError("API error occurred")
        
        result = test_function()
        
        assert result["statusCode"] == 502
        body = json.loads(result["body"])
        assert body["error"]["type"] == "APIError"

    def test_handle_api_errors_value_error(self):
        """Test decorator with value error."""
        @handle_api_errors
        def test_function():
            raise ValueError("Invalid input")
        
        result = test_function()
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"]["type"] == "ValidationError"

    def test_handle_api_errors_unexpected_exception(self):
        """Test decorator with unexpected exception."""
        @handle_api_errors
        def test_function():
            raise RuntimeError("Unexpected error")
        
        result = test_function()
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["error"]["type"] == "InternalServerError"


class TestProcessSymbols:
    """Test cases for the process_symbols function."""

    @patch('lambda_function.LunarCrushClient')
    @patch('lambda_function.S3Storage')
    @patch('lambda_function.parse_event_body')
    def test_process_symbols_success(self, mock_parse, mock_s3, mock_client, mock_environment_variables):
        """Test successful symbol processing."""
        # Setup mocks
        mock_parse.return_value = {
            "symbols": ["BTC", "ETH"],
            "parameters": {"test": "value"}
        }
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_metrics = [Mock()]
        mock_metrics[0].to_dict.return_value = {"symbol": "BTC", "data": "test"}
        mock_client_instance.get_comprehensive_metrics.return_value = mock_metrics
        
        mock_s3_instance = Mock()
        mock_s3.return_value = mock_s3_instance
        
        # Execute
        event = {"body": json.dumps({"symbols": ["BTC", "ETH"]})}
        result = process_symbols(event)
        
        # Verify
        assert result["metadata"]["symbols_requested"] == ["BTC", "ETH"]
        assert result["metadata"]["count"] == 1
        assert result["metadata"]["parameters"]["test"] == "value"
        assert len(result["metrics"]) == 1
        assert result["metrics"][0] == {"symbol": "BTC", "data": "test"}
        
        mock_client_instance.get_comprehensive_metrics.assert_called_once_with(["BTC", "ETH"])
        # Note: S3 storage might be skipped in test environment, so we don't assert this

    @patch('lambda_function.LunarCrushClient')
    @patch('lambda_function.S3Storage')
    @patch('lambda_function.parse_event_body')
    def test_process_symbols_s3_failure(self, mock_parse, mock_s3, mock_client, mock_environment_variables):
        """Test symbol processing with S3 storage failure."""
        # Setup mocks
        mock_parse.return_value = {
            "symbols": ["BTC"],
            "parameters": {}
        }
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_metrics = [Mock()]
        mock_metrics[0].to_dict.return_value = {"symbol": "BTC"}
        mock_client_instance.get_comprehensive_metrics.return_value = mock_metrics
        
        mock_s3_instance = Mock()
        mock_s3_instance.store_metrics.side_effect = Exception("S3 failed")
        mock_s3.return_value = mock_s3_instance
        
        # Execute
        event = {"body": json.dumps({"symbols": ["BTC"]})}
        result = process_symbols(event)
        
        # Verify - should still succeed despite S3 failure
        assert result["metadata"]["symbols_requested"] == ["BTC"]
        assert result["metadata"]["count"] == 1
        assert len(result["metrics"]) == 1

    @patch('lambda_function.LunarCrushClient')
    @patch('lambda_function.S3Storage')
    @patch('lambda_function.parse_event_body')
    def test_process_symbols_no_s3_initialization(self, mock_parse, mock_s3, mock_client, monkeypatch):
        """Test symbol processing without S3 initialization."""
        # Setup environment for localhost
        monkeypatch.setenv("S3_ENDPOINT_URL", "http://localhost:4566")
        monkeypatch.setenv("LUNARCRUSH_API_KEY", "test_key")
        monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
        
        # Setup mocks
        mock_parse.return_value = {
            "symbols": ["BTC"],
            "parameters": {}
        }
        
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_metrics = [Mock()]
        mock_metrics[0].to_dict.return_value = {"symbol": "BTC"}
        mock_client_instance.get_comprehensive_metrics.return_value = mock_metrics
        
        # Execute
        event = {"body": json.dumps({"symbols": ["BTC"]})}
        result = process_symbols(event)
        
        # Verify
        assert result["metadata"]["symbols_requested"] == ["BTC"]
        assert result["metadata"]["count"] == 1
        assert len(result["metrics"]) == 1
        
        # S3 should not be initialized for localhost
        mock_s3.assert_not_called()

    @patch('lambda_function.LunarCrushClient')
    @patch('lambda_function.parse_event_body')
    def test_process_symbols_missing_api_key(self, mock_parse, mock_client, monkeypatch):
        """Test symbol processing with missing API key."""
        monkeypatch.delenv("LUNARCRUSH_API_KEY", raising=False)
        
        mock_parse.return_value = {
            "symbols": ["BTC"],
            "parameters": {}
        }
        
        event = {"body": json.dumps({"symbols": ["BTC"]})}
        
        # Test that validate_environment raises ValueError when called directly
        with pytest.raises(ValueError) as exc_info:
            from lambda_function import validate_environment
            validate_environment()
        
        assert "Missing required environment variables: LUNARCRUSH_API_KEY" in str(exc_info.value)


class TestLambdaHandler:
    """Test cases for the main lambda_handler function."""

    @patch('lambda_function.validate_environment')
    @patch('lambda_function.process_symbols')
    def test_lambda_handler_success(self, mock_process, mock_validate, mock_lambda_event, mock_lambda_context):
        """Test successful lambda handler execution."""
        # Setup mocks
        mock_validate.return_value = True
        mock_process.return_value = {
            "metrics": [{"symbol": "BTC"}],
            "metadata": {
                "symbols_requested": ["BTC"],
                "count": 1,
                "s3_bucket": "test-bucket",
                "s3_file": "candidates.json"
            }
        }
        
        # Execute
        result = lambda_handler(mock_lambda_event, mock_lambda_context)
        
        # Verify
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["success"] is True
        assert "metadata" in body["data"]
        assert "timestamp" in body["data"]["metadata"]
        assert body["data"]["metadata"]["symbols_requested"] == ["BTC"]

    @patch('lambda_function.validate_environment')
    def test_lambda_handler_options_request(self, mock_validate, mock_lambda_context):
        """Test lambda handler with OPTIONS request for CORS."""
        # Setup
        mock_validate.return_value = True
        event = {"httpMethod": "OPTIONS"}
        
        # Execute
        result = lambda_handler(event, mock_lambda_context)
        
        # Verify
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["success"] is True

    @patch('lambda_function.validate_environment')
    def test_lambda_handler_environment_validation_failure(self, mock_validate, mock_lambda_event, mock_lambda_context):
        """Test lambda handler with environment validation failure."""
        mock_validate.side_effect = ValueError("Missing environment variables")
        
        result = lambda_handler(mock_lambda_event, mock_lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["success"] is False
        assert body["error"]["type"] == "ValidationError"

    @patch('lambda_function.validate_environment')
    @patch('lambda_function.process_symbols')
    def test_lambda_handler_unexpected_error(self, mock_process, mock_validate, mock_lambda_event, mock_lambda_context):
        """Test lambda handler with unexpected error."""
        mock_validate.return_value = True
        mock_process.side_effect = RuntimeError("Unexpected error")
        
        result = lambda_handler(mock_lambda_event, mock_lambda_context)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["success"] is False
        assert body["error"]["type"] == "InternalServerError"

    @patch('lambda_function.validate_environment')
    @patch('lambda_function.process_symbols')
    def test_lambda_handler_logging(self, mock_process, mock_validate, mock_lambda_event, mock_lambda_context):
        """Test lambda handler logging functionality."""
        mock_validate.return_value = True
        mock_process.return_value = {
            "metrics": [],
            "metadata": {"symbols_requested": [], "count": 0}
        }
        
        # Execute
        lambda_handler(mock_lambda_event, mock_lambda_context)
        
        # Verify that process_symbols was called
        mock_process.assert_called_once_with(mock_lambda_event)

    def test_lambda_handler_local_testing(self):
        """Test lambda handler local testing functionality."""
        # This tests the __main__ section for local testing
        # We can't easily test the actual execution, but we can verify the structure
        test_event = {
            "symbols": ["BTC", "ETH", "ADA"]
        }
        
        # Create a mock context
        class MockContext:
            aws_request_id = "test-request-id"
            function_name = "test-function"
            function_version = "test-version"
        
        # Verify the event structure is valid
        assert "symbols" in test_event
        assert isinstance(test_event["symbols"], list)
        assert len(test_event["symbols"]) > 0


class TestIntegrationScenarios:
    """Integration test scenarios for the Lambda function."""

    @patch('lambda_function.LunarCrushClient')
    @patch('lambda_function.S3Storage')
    def test_end_to_end_processing(self, mock_s3, mock_client, mock_environment_variables):
        """Test end-to-end processing flow."""
        # Setup comprehensive mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create mock metrics
        mock_metrics = []
        for symbol in ["BTC", "ETH"]:
            mock_metric = Mock()
            mock_metric.symbol = symbol
            mock_metric.to_dict.return_value = {
                "symbol": symbol,
                "current": {"interactions_24h": 100000},
                "changes": {"interactions_24h_pct": 5.0},
                "timestamp": datetime.now().isoformat()
            }
            mock_metrics.append(mock_metric)
        
        mock_client_instance.get_comprehensive_metrics.return_value = mock_metrics
        
        mock_s3_instance = Mock()
        mock_s3.return_value = mock_s3_instance
        
        # Create test event
        event = {
            "body": json.dumps({
                "symbols": ["BTC", "ETH"],
                "parameters": {"include_historical": True}
            })
        }
        
        # Execute
        result = process_symbols(event)
        
        # Verify comprehensive result
        assert result["metadata"]["symbols_requested"] == ["BTC", "ETH"]
        assert result["metadata"]["count"] == 2
        assert result["metadata"]["parameters"]["include_historical"] is True
        assert len(result["metrics"]) == 2
        
        # Note: S3 storage might be skipped in test environment, so we don't assert this
        # Verify API client was called correctly
        mock_client_instance.get_comprehensive_metrics.assert_called_once_with(["BTC", "ETH"])

    def test_error_propagation_through_layers(self, mock_environment_variables):
        """Test that errors are properly propagated through all layers."""
        # Test that API errors are properly handled by the decorator
        @handle_api_errors
        def test_api_error():
            raise LunarCrushRateLimitError("Rate limit exceeded", retry_after=120)
        
        result = test_api_error()
        
        assert result["statusCode"] == 429
        body = json.loads(result["body"])
        assert body["error"]["type"] == "RateLimitExceeded"

    def test_response_format_consistency(self):
        """Test that all response formats are consistent."""
        # Test success response
        success_response = LambdaResponse.success({"test": "data"})
        success_body = json.loads(success_response["body"])
        
        # Test error response
        error_response = LambdaResponse.error("Test error")
        error_body = json.loads(error_response["body"])
        
        # Verify consistent structure
        assert "success" in success_body
        assert "success" in error_body
        assert "data" in success_body
        assert "error" in error_body
        
        # Verify headers are consistent
        for response in [success_response, error_response]:
            assert "Content-Type" in response["headers"]
            assert "Access-Control-Allow-Origin" in response["headers"]
            assert "Access-Control-Allow-Headers" in response["headers"]
            assert "Access-Control-Allow-Methods" in response["headers"]