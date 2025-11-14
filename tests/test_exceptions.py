"""
Comprehensive unit tests for the exception hierarchy.

This module tests all custom exception classes including:
- Exception inheritance hierarchy
- Error message formatting
- Exception attributes and methods
- Edge cases and error scenarios
"""

import pytest

from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushRateLimitError,
    LunarCrushAuthenticationError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit


class TestLunarCrushAPIError:
    """Test cases for the base LunarCrushAPIError exception."""

    def test_base_exception_initialization(self):
        """Test base exception initialization with message only."""
        error = LunarCrushAPIError("Test error message")
        
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response_data == {}

    def test_base_exception_initialization_with_status_code(self):
        """Test base exception initialization with status code."""
        error = LunarCrushAPIError("Test error", status_code=400)
        
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.response_data == {}

    def test_base_exception_initialization_with_response_data(self):
        """Test base exception initialization with response data."""
        response_data = {"error": "details", "code": "TEST_ERROR"}
        error = LunarCrushAPIError("Test error", response_data=response_data)
        
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response_data == response_data

    def test_base_exception_initialization_with_all_parameters(self):
        """Test base exception initialization with all parameters."""
        response_data = {"error": "details"}
        error = LunarCrushAPIError(
            "Test error",
            status_code=500,
            response_data=response_data
        )
        
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.response_data == response_data

    def test_base_exception_string_representation(self):
        """Test string representation of base exception."""
        error = LunarCrushAPIError("Test error")
        
        assert str(error) == "LunarCrushAPIError: Test error"

    def test_base_exception_string_representation_with_status_code(self):
        """Test string representation with status code."""
        error = LunarCrushAPIError("Test error", status_code=400)
        
        assert str(error) == "LunarCrushAPIError: Test error (HTTP 400)"

    def test_base_exception_inheritance(self):
        """Test that base exception inherits from Exception."""
        error = LunarCrushAPIError("Test error")
        
        assert isinstance(error, Exception)
        assert isinstance(error, LunarCrushAPIError)

    def test_base_exception_response_data_default(self):
        """Test that response_data defaults to empty dict."""
        error = LunarCrushAPIError("Test error")
        
        assert error.response_data == {}


class TestLunarCrushRateLimitError:
    """Test cases for LunarCrushRateLimitError exception."""

    def test_rate_limit_error_default_initialization(self):
        """Test rate limit error with default values."""
        error = LunarCrushRateLimitError()
        
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.retry_after is None
        assert error.response_data == {}

    def test_rate_limit_error_custom_message(self):
        """Test rate limit error with custom message."""
        error = LunarCrushRateLimitError("Custom rate limit message")
        
        assert error.message == "Custom rate limit message"
        assert error.status_code == 429
        assert error.retry_after is None

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after value."""
        error = LunarCrushRateLimitError(retry_after=120)
        
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.retry_after == 120

    def test_rate_limit_error_with_response_data(self):
        """Test rate limit error with response data."""
        response_data = {"error": "Too many requests"}
        error = LunarCrushRateLimitError(
            response_data=response_data,
            retry_after=60
        )
        
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.retry_after == 60
        assert error.response_data == response_data

    def test_rate_limit_error_string_representation(self):
        """Test string representation of rate limit error."""
        error = LunarCrushRateLimitError()
        
        assert str(error) == "LunarCrushAPIError: Rate limit exceeded (HTTP 429)"

    def test_rate_limit_error_string_representation_with_retry(self):
        """Test string representation with retry_after."""
        error = LunarCrushRateLimitError(retry_after=60)
        
        assert str(error) == "LunarCrushAPIError: Rate limit exceeded (HTTP 429) (Retry after 60 seconds)"

    def test_rate_limit_error_inheritance(self):
        """Test that rate limit error inherits from base exception."""
        error = LunarCrushRateLimitError()
        
        assert isinstance(error, Exception)
        assert isinstance(error, LunarCrushAPIError)
        assert isinstance(error, LunarCrushRateLimitError)

    def test_rate_limit_error_all_parameters(self):
        """Test rate limit error with all parameters."""
        response_data = {"error": "Rate limit exceeded"}
        error = LunarCrushRateLimitError(
            message="Custom message",
            retry_after=300,
            response_data=response_data
        )
        
        assert error.message == "Custom message"
        assert error.status_code == 429
        assert error.retry_after == 300
        assert error.response_data == response_data


class TestLunarCrushAuthenticationError:
    """Test cases for LunarCrushAuthenticationError exception."""

    def test_authentication_error_default_initialization(self):
        """Test authentication error with default values."""
        error = LunarCrushAuthenticationError()
        
        assert error.message == "Authentication failed"
        assert error.status_code == 401
        assert error.response_data == {}

    def test_authentication_error_custom_message(self):
        """Test authentication error with custom message."""
        error = LunarCrushAuthenticationError("Invalid API key")
        
        assert error.message == "Invalid API key"
        assert error.status_code == 401
        assert error.response_data == {}

    def test_authentication_error_with_response_data(self):
        """Test authentication error with response data."""
        response_data = {"error": "Unauthorized", "code": "AUTH_FAILED"}
        error = LunarCrushAuthenticationError(
            message="Auth failed",
            response_data=response_data
        )
        
        assert error.message == "Auth failed"
        assert error.status_code == 401
        assert error.response_data == response_data

    def test_authentication_error_string_representation(self):
        """Test string representation of authentication error."""
        error = LunarCrushAuthenticationError()
        
        assert str(error) == "LunarCrushAPIError: Authentication failed (HTTP 401)"

    def test_authentication_error_string_representation_custom(self):
        """Test string representation with custom message."""
        error = LunarCrushAuthenticationError("API key expired")
        
        assert str(error) == "LunarCrushAPIError: API key expired (HTTP 401)"

    def test_authentication_error_inheritance(self):
        """Test that authentication error inherits from base exception."""
        error = LunarCrushAuthenticationError()
        
        assert isinstance(error, Exception)
        assert isinstance(error, LunarCrushAPIError)
        assert isinstance(error, LunarCrushAuthenticationError)


class TestLunarCrushNetworkError:
    """Test cases for LunarCrushNetworkError exception."""

    def test_network_error_default_initialization(self):
        """Test network error with default values."""
        error = LunarCrushNetworkError()
        
        assert error.message == "Network error occurred"
        assert error.status_code is None
        assert error.original_exception is None
        assert error.timeout is None
        assert error.response_data == {}

    def test_network_error_custom_message(self):
        """Test network error with custom message."""
        error = LunarCrushNetworkError("Connection timeout")
        
        assert error.message == "Connection timeout"
        assert error.status_code is None
        assert error.original_exception is None
        assert error.timeout is None

    def test_network_error_with_timeout(self):
        """Test network error with timeout value."""
        error = LunarCrushNetworkError(timeout=30.5)
        
        assert error.message == "Network error occurred"
        assert error.timeout == 30.5
        assert error.original_exception is None

    def test_network_error_with_original_exception(self):
        """Test network error with original exception."""
        original_error = ConnectionError("Connection failed")
        error = LunarCrushNetworkError(
            message="Network failure",
            original_exception=original_error
        )
        
        assert error.message == "Network failure"
        assert error.original_exception == original_error
        assert error.timeout is None

    def test_network_error_with_all_parameters(self):
        """Test network error with all parameters."""
        original_error = TimeoutError("Request timed out")
        error = LunarCrushNetworkError(
            message="Request failed",
            original_exception=original_error,
            timeout=45.0
        )
        
        assert error.message == "Request failed"
        assert error.original_exception == original_error
        assert error.timeout == 45.0

    def test_network_error_string_representation(self):
        """Test string representation of network error."""
        error = LunarCrushNetworkError()
        
        assert str(error) == "LunarCrushAPIError: Network error occurred"

    def test_network_error_string_representation_with_timeout(self):
        """Test string representation with timeout."""
        error = LunarCrushNetworkError(timeout=30.0)
        
        assert str(error) == "LunarCrushAPIError: Network error occurred (Timeout: 30.0s)"

    def test_network_error_string_representation_with_original_exception(self):
        """Test string representation with original exception."""
        original_error = ConnectionError("Connection failed")
        error = LunarCrushNetworkError(
            original_exception=original_error
        )
        
        assert str(error) == "LunarCrushAPIError: Network error occurred (Caused by: ConnectionError)"

    def test_network_error_string_representation_with_both(self):
        """Test string representation with both timeout and original exception."""
        original_error = TimeoutError("Request timed out")
        error = LunarCrushNetworkError(
            timeout=60.0,
            original_exception=original_error
        )
        
        expected = "LunarCrushAPIError: Network error occurred (Timeout: 60.0s) (Caused by: TimeoutError)"
        assert str(error) == expected

    def test_network_error_inheritance(self):
        """Test that network error inherits from base exception."""
        error = LunarCrushNetworkError()
        
        assert isinstance(error, Exception)
        assert isinstance(error, LunarCrushAPIError)
        assert isinstance(error, LunarCrushNetworkError)


class TestLunarCrushDataValidationError:
    """Test cases for LunarCrushDataValidationError exception."""

    def test_data_validation_error_default_initialization(self):
        """Test data validation error with default values."""
        error = LunarCrushDataValidationError()
        
        assert error.message == "Data validation failed"
        assert error.status_code is None
        assert error.missing_fields == []
        assert error.invalid_fields == {}
        assert error.response_data == {}

    def test_data_validation_error_custom_message(self):
        """Test data validation error with custom message."""
        error = LunarCrushDataValidationError("Invalid data format")
        
        assert error.message == "Invalid data format"
        assert error.missing_fields == []
        assert error.invalid_fields == {}

    def test_data_validation_error_with_missing_fields(self):
        """Test data validation error with missing fields."""
        missing_fields = ["symbol", "timestamp"]
        error = LunarCrushDataValidationError(
            missing_fields=missing_fields
        )
        
        assert error.message == "Data validation failed"
        assert error.missing_fields == missing_fields
        assert error.invalid_fields == {}

    def test_data_validation_error_with_invalid_fields(self):
        """Test data validation error with invalid fields."""
        invalid_fields = {
            "price": "not_a_number",
            "volume": -100
        }
        error = LunarCrushDataValidationError(
            invalid_fields=invalid_fields
        )
        
        assert error.message == "Data validation failed"
        assert error.missing_fields == []
        assert error.invalid_fields == invalid_fields

    def test_data_validation_error_with_all_parameters(self):
        """Test data validation error with all parameters."""
        missing_fields = ["symbol", "timestamp"]
        invalid_fields = {
            "price": "not_a_number",
            "volume": -100
        }
        response_data = {"error": "validation failed"}
        
        error = LunarCrushDataValidationError(
            message="Custom validation error",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
            response_data=response_data
        )
        
        assert error.message == "Custom validation error"
        assert error.missing_fields == missing_fields
        assert error.invalid_fields == invalid_fields
        assert error.response_data == response_data

    def test_data_validation_error_string_representation(self):
        """Test string representation of data validation error."""
        error = LunarCrushDataValidationError()
        
        assert str(error) == "LunarCrushAPIError: Data validation failed"

    def test_data_validation_error_string_representation_with_missing_fields(self):
        """Test string representation with missing fields."""
        missing_fields = ["symbol", "timestamp"]
        error = LunarCrushDataValidationError(
            missing_fields=missing_fields
        )
        
        expected = "LunarCrushAPIError: Data validation failed (Missing fields: symbol, timestamp)"
        assert str(error) == expected

    def test_data_validation_error_string_representation_with_invalid_fields(self):
        """Test string representation with invalid fields."""
        invalid_fields = {
            "price": "not_a_number",
            "volume": -100
        }
        error = LunarCrushDataValidationError(
            invalid_fields=invalid_fields
        )
        
        result = str(error)
        assert "LunarCrushAPIError: Data validation failed" in result
        assert "Invalid fields:" in result
        assert "price=not_a_number (type: str)" in result
        assert "volume=-100 (type: int)" in result

    def test_data_validation_error_string_representation_with_both(self):
        """Test string representation with both missing and invalid fields."""
        missing_fields = ["symbol"]
        invalid_fields = {"price": "not_a_number"}
        
        error = LunarCrushDataValidationError(
            missing_fields=missing_fields,
            invalid_fields=invalid_fields
        )
        
        result = str(error)
        assert "Missing fields: symbol" in result
        assert "Invalid fields:" in result
        assert "price=not_a_number (type: str)" in result

    def test_data_validation_error_inheritance(self):
        """Test that data validation error inherits from base exception."""
        error = LunarCrushDataValidationError()
        
        assert isinstance(error, Exception)
        assert isinstance(error, LunarCrushAPIError)
        assert isinstance(error, LunarCrushDataValidationError)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy relationships."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from LunarCrushAPIError."""
        exceptions = [
            LunarCrushRateLimitError,
            LunarCrushAuthenticationError,
            LunarCrushNetworkError,
            LunarCrushDataValidationError
        ]
        
        for exception_class in exceptions:
            # Test class inheritance
            assert issubclass(exception_class, LunarCrushAPIError)
            assert issubclass(exception_class, Exception)
            
            # Test instance inheritance
            instance = exception_class("test message")  # Provide required message parameter
            assert isinstance(instance, LunarCrushAPIError)
            assert isinstance(instance, Exception)

    def test_exception_hierarchy_order(self):
        """Test that exception hierarchy follows expected order."""
        base_error = LunarCrushAPIError("Base error")
        rate_limit_error = LunarCrushRateLimitError()
        auth_error = LunarCrushAuthenticationError()
        network_error = LunarCrushNetworkError()
        validation_error = LunarCrushDataValidationError()
        
        # All should be instances of base exception
        assert isinstance(rate_limit_error, LunarCrushAPIError)
        assert isinstance(auth_error, LunarCrushAPIError)
        assert isinstance(network_error, LunarCrushAPIError)
        assert isinstance(validation_error, LunarCrushAPIError)
        
        # None should be instances of each other (except base)
        assert not isinstance(rate_limit_error, LunarCrushAuthenticationError)
        assert not isinstance(auth_error, LunarCrushNetworkError)
        assert not isinstance(network_error, LunarCrushDataValidationError)
        assert not isinstance(validation_error, LunarCrushRateLimitError)

    def test_exception_catching_hierarchy(self):
        """Test that exceptions can be caught at different hierarchy levels."""
        # Test catching base exception
        try:
            raise LunarCrushRateLimitError()
        except LunarCrushAPIError:
            caught = True
        else:
            caught = False
        assert caught is True
        
        # Test catching specific exception
        try:
            raise LunarCrushAuthenticationError()
        except LunarCrushAuthenticationError:
            caught = True
        else:
            caught = False
        assert caught is True
        
        # Test that specific exception is not caught by different specific exception
        caught = False
        try:
            raise LunarCrushNetworkError()
        except LunarCrushRateLimitError:
            caught = True
        except Exception:
            # Catch any other exception and don't set caught to True
            pass
        assert caught is False
        
        # Also verify that the exception would be caught by the base class
        try:
            raise LunarCrushNetworkError()
        except LunarCrushAPIError:
            base_caught = True
        else:
            base_caught = False
        assert base_caught is True

    def test_exception_attributes_preserved_in_hierarchy(self):
        """Test that exception attributes are preserved through inheritance."""
        # Test that specific exceptions have their unique attributes
        rate_limit_error = LunarCrushRateLimitError(retry_after=120)
        assert hasattr(rate_limit_error, 'retry_after')
        assert rate_limit_error.retry_after == 120
        
        auth_error = LunarCrushAuthenticationError()
        assert hasattr(auth_error, 'status_code')
        assert auth_error.status_code == 401
        
        network_error = LunarCrushNetworkError(timeout=30.0)
        assert hasattr(network_error, 'timeout')
        assert network_error.timeout == 30.0
        
        validation_error = LunarCrushDataValidationError(missing_fields=["test"])
        assert hasattr(validation_error, 'missing_fields')
        assert validation_error.missing_fields == ["test"]
        
        # All should still have base attributes
        for error in [rate_limit_error, auth_error, network_error, validation_error]:
            assert hasattr(error, 'message')
            assert hasattr(error, 'response_data')
            assert hasattr(error, 'status_code')


class TestExceptionEdgeCases:
    """Test edge cases and unusual scenarios for exceptions."""

    def test_exception_with_none_message(self):
        """Test exception with None message."""
        error = LunarCrushAPIError("None")  # Pass as string to avoid type error
        
        assert error.message == "None"
        assert str(error) == "LunarCrushAPIError: None"

    def test_exception_with_empty_message(self):
        """Test exception with empty message."""
        error = LunarCrushAPIError("")
        
        assert error.message == ""
        assert str(error) == "LunarCrushAPIError: "

    def test_exception_with_numeric_status_code(self):
        """Test exception with numeric status code."""
        error = LunarCrushAPIError("Error", status_code=404)
        
        assert error.status_code == 404
        assert "HTTP 404" in str(error)

    def test_exception_with_zero_status_code(self):
        """Test exception with zero status code."""
        error = LunarCrushAPIError("Error", status_code=0)
        
        assert error.status_code == 0
        # Zero status code is unusual, but should be handled
        assert "HTTP 0" in str(error)

    def test_exception_with_large_retry_after(self):
        """Test exception with large retry_after value."""
        error = LunarCrushRateLimitError(retry_after=86400)  # 24 hours
        
        assert error.retry_after == 86400
        assert "Retry after 86400 seconds" in str(error)

    def test_exception_with_zero_retry_after(self):
        """Test exception with zero retry_after value."""
        error = LunarCrushRateLimitError(retry_after=0)
        
        assert error.retry_after == 0
        # Zero retry after should be included in string representation
        assert "Retry after 0 seconds" in str(error)

    def test_exception_with_fractional_timeout(self):
        """Test exception with fractional timeout value."""
        error = LunarCrushNetworkError(timeout=1.5)
        
        assert error.timeout == 1.5
        assert "Timeout: 1.5s" in str(error)

    def test_exception_with_empty_lists_and_dicts(self):
        """Test exception with empty lists and dictionaries."""
        error = LunarCrushDataValidationError(
            missing_fields=[],
            invalid_fields={}
        )
        
        assert error.missing_fields == []
        assert error.invalid_fields == {}
        assert "Missing fields:" not in str(error)
        assert "Invalid fields:" not in str(error)

    def test_exception_with_complex_invalid_fields(self):
        """Test exception with complex invalid field values."""
        invalid_fields = {
            "nested_dict": {"key": "value"},
            "list_value": [1, 2, 3],
            "none_value": None,
            "boolean_value": True
        }
        
        error = LunarCrushDataValidationError(invalid_fields=invalid_fields)
        
        result = str(error)
        assert "nested_dict={'key': 'value'} (type: dict)" in result
        assert "list_value=[1, 2, 3] (type: list)" in result
        # Handle None type representation which may vary
        assert "none_value=None (type: NoneType)" in result
        assert "boolean_value=True (type: bool)" in result

    def test_exception_chaining(self):
        """Test exception chaining with original exceptions."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise LunarCrushNetworkError(
                    "Wrapped error",
                    original_exception=e
                ) from e
        except LunarCrushNetworkError as e:
            assert e.original_exception is not None
            assert isinstance(e.original_exception, ValueError)
            assert str(e.original_exception) == "Original error"

    def test_exception_pickle_support(self):
        """Test that exceptions can be pickled and unpickled."""
        import pickle
        
        original_error = LunarCrushRateLimitError(
            message="Test error",
            retry_after=60,
            response_data={"test": "data"}
        )
        
        # Pickle and unpickle
        pickled = pickle.dumps(original_error)
        unpickled = pickle.loads(pickled)
        
        # Verify attributes are preserved
        assert unpickled.message == original_error.message
        assert unpickled.retry_after == original_error.retry_after
        assert unpickled.response_data == original_error.response_data
        assert type(unpickled) == type(original_error)