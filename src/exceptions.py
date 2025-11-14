"""
Custom exceptions for the LunarCrush API integration.

This module defines a hierarchy of custom exceptions for handling
different types of errors that can occur when interacting with the
LunarCrush API.
"""

from typing import Optional, Any


class LunarCrushAPIError(Exception):
    """
    Base exception for all LunarCrush API related errors.
    
    This is the root exception class for all LunarCrush API errors.
    Specific error types inherit from this base class.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[dict] = None
    ) -> None:
        """
        Initialize LunarCrushAPIError.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code if applicable
            response_data: Raw response data from the API
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_msg = f"LunarCrushAPIError: {self.message}"
        if self.status_code is not None:  # Check for None, not just truthy
            base_msg += f" (HTTP {self.status_code})"
        return base_msg


class LunarCrushRateLimitError(LunarCrushAPIError):
    """
    Exception raised when API rate limit is exceeded.
    
    This exception is raised when the LunarCrush API returns a 429 
    Too Many Requests response, indicating that the rate limit has been
    exceeded and the client should wait before making additional requests.
    """
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        response_data: Optional[dict] = None
    ) -> None:
        """
        Initialize LunarCrushRateLimitError.
        
        Args:
            message: Human-readable error message
            retry_after: Number of seconds to wait before retrying
            response_data: Raw response data from the API
        """
        super().__init__(message, status_code=429, response_data=response_data)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_msg = super().__str__()
        if self.retry_after is not None:  # Check for None, not just truthy
            base_msg += f" (Retry after {self.retry_after} seconds)"
        return base_msg


class LunarCrushAuthenticationError(LunarCrushAPIError):
    """
    Exception raised when API authentication fails.
    
    This exception is raised when the LunarCrush API returns a 401 
    Unauthorized response, indicating that the API key is invalid,
    expired, or missing.
    """
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        response_data: Optional[dict] = None
    ) -> None:
        """
        Initialize LunarCrushAuthenticationError.
        
        Args:
            message: Human-readable error message
            response_data: Raw response data from the API
        """
        super().__init__(message, status_code=401, response_data=response_data)


class LunarCrushNetworkError(LunarCrushAPIError):
    """
    Exception raised when network connectivity issues occur.
    
    This exception is raised when there are connection problems,
    timeouts, or other network-related issues preventing communication
    with the LunarCrush API.
    """
    
    def __init__(
        self, 
        message: str = "Network error occurred",
        original_exception: Optional[Exception] = None,
        timeout: Optional[float] = None
    ) -> None:
        """
        Initialize LunarCrushNetworkError.
        
        Args:
            message: Human-readable error message
            original_exception: The original exception that caused this error
            timeout: Timeout value in seconds if applicable
        """
        super().__init__(message, status_code=None)
        self.original_exception = original_exception
        self.timeout = timeout
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_msg = super().__str__()
        if self.timeout:
            base_msg += f" (Timeout: {self.timeout}s)"
        if self.original_exception:
            base_msg += f" (Caused by: {type(self.original_exception).__name__})"
        return base_msg


class LunarCrushDataValidationError(LunarCrushAPIError):
    """
    Exception raised when API response data validation fails.
    
    This exception is raised when the API response doesn't match the
    expected schema, contains invalid data types, or is missing required
    fields for processing.
    """
    
    def __init__(
        self, 
        message: str = "Data validation failed",
        missing_fields: Optional[list] = None,
        invalid_fields: Optional[dict] = None,
        response_data: Optional[dict] = None
    ) -> None:
        """
        Initialize LunarCrushDataValidationError.
        
        Args:
            message: Human-readable error message
            missing_fields: List of required fields that are missing
            invalid_fields: Dictionary of invalid fields with their values
            response_data: Raw response data from the API
        """
        super().__init__(message, status_code=None, response_data=response_data)
        self.missing_fields = missing_fields or []
        self.invalid_fields = invalid_fields or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        base_msg = super().__str__()
        if self.missing_fields:
            base_msg += f" (Missing fields: {', '.join(self.missing_fields)})"
        if self.invalid_fields:
            field_details = []
            for field, value in self.invalid_fields.items():
                # Handle None type representation consistently
                value_type = type(value).__name__ if value is not None else "NoneType"
                field_details.append(f"{field}={value} (type: {value_type})")
            base_msg += f" (Invalid fields: {', '.join(field_details)})"
        return base_msg