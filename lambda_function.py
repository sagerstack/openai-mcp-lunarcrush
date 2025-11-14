import json
import logging
import os
import sys
from typing import Dict, Any, Optional, List

# Load environment variables from .env.local file
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    # Fallback if dotenv is not available
    pass

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushRateLimitError,
    LunarCrushAuthenticationError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)
from src.lunarcrush_client import LunarCrushClient, SocialMetrics
from src.adapters.s3_storage import S3Storage

# Initialize structured logging
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

class LambdaResponse:
    """Helper class for creating standardized Lambda responses."""
    
    @staticmethod
    def success(data: Any, status_code: int = 200) -> Dict[str, Any]:
        """Create a successful Lambda response."""
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
            },
            "body": json.dumps({
                "success": True,
                "data": data
            }, default=str)
        }
    
    @staticmethod
    def error(message: str, status_code: int = 500, error_type: str = "InternalServerError") -> Dict[str, Any]:
        """Create an error Lambda response."""
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
            },
            "body": json.dumps({
                "success": False,
                "error": {
                    "type": error_type,
                    "message": message
                }
            })
        }




def validate_environment() -> bool:
    """Validate that required environment variables are set.

    Returns:
        bool: True if all required environment variables are present

    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = ["LUNARCRUSH_API_KEY", "S3_BUCKET_NAME"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    return True


def parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and validate the Lambda event body.

    Args:
        event: Lambda event dictionary

    Returns:
        Parsed event body as dictionary

    Raises:
        ValueError: If event body is invalid
    """
    try:
        # Handle different event sources (API Gateway, Lambda URL, etc.)
        if "body" in event:
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]
        else:
            # For direct invocation or other event sources
            body = event

        # Extract symbols from the body
        symbols = body.get("symbols")
        if not symbols:
            # Default to symbols from environment if not provided
            symbols_env = os.getenv("SYMBOLS_LIST", "BTC,ETH,ADA,DOT,LINK")
            symbols = [s.strip().upper() for s in symbols_env.split(",")]

        # Validate symbols
        if not isinstance(symbols, list):
            raise ValueError("Symbols must be a list")

        if not symbols:
            raise ValueError("At least one symbol must be provided")

        # Validate each symbol
        validated_symbols = []
        for symbol in symbols:
            if not isinstance(symbol, str):
                raise ValueError(f"Symbol must be a string: {symbol}")

            symbol = symbol.strip().upper()
            if not symbol:
                continue  # Skip empty strings

            # Basic symbol validation (alphanumeric only)
            if not symbol.replace("-", "").isalnum():
                raise ValueError(f"Invalid symbol format: {symbol}")

            validated_symbols.append(symbol)

        if not validated_symbols:
            raise ValueError("No valid symbols provided")

        return {
            "symbols": validated_symbols,
            "parameters": body.get("parameters", {})
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in event body: {e}")
        raise ValueError(f"Invalid JSON in request body: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing event body: {e}")
        raise ValueError(f"Error parsing request body: {str(e)}")

def handle_api_errors(func):
    """Decorator to handle API errors and convert them to Lambda responses."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LunarCrushRateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            return LambdaResponse.error(
                message=f"Rate limit exceeded. Retry after {e.retry_after} seconds.",
                status_code=429,
                error_type="RateLimitExceeded"
            )
        except LunarCrushAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return LambdaResponse.error(
                message="Authentication failed. Please check your API key.",
                status_code=401,
                error_type="AuthenticationError"
            )
        except LunarCrushNetworkError as e:
            logger.error(f"Network error: {e}")
            return LambdaResponse.error(
                message="Network connectivity error occurred.",
                status_code=503,
                error_type="NetworkError"
            )
        except LunarCrushDataValidationError as e:
            logger.error(f"Data validation error: {e}")
            return LambdaResponse.error(
                message="Invalid data received from API.",
                status_code=422,
                error_type="DataValidationError"
            )
        except LunarCrushAPIError as e:
            logger.error(f"API error: {e}")
            # Check status code to determine specific error type
            if e.status_code == 401:
                return LambdaResponse.error(
                    message="Authentication failed. Please check your API key.",
                    status_code=401,
                    error_type="AuthenticationError"
                )
            elif e.status_code == 429:
                return LambdaResponse.error(
                    message="Rate limit exceeded. Please try again later.",
                    status_code=429,
                    error_type="RateLimitExceeded"
                )
            elif e.status_code and e.status_code >= 500:
                return LambdaResponse.error(
                    message="API server error occurred.",
                    status_code=502,
                    error_type="APIError"
                )
            else:
                return LambdaResponse.error(
                    message="An error occurred while fetching data from the API.",
                    status_code=502,
                    error_type="APIError"
                )
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return LambdaResponse.error(
                message=str(e),
                status_code=400,
                error_type="ValidationError"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return LambdaResponse.error(
                message="An unexpected error occurred.",
                status_code=500,
                error_type="InternalServerError"
            )
    return wrapper


def process_symbols(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process cryptocurrency symbols and fetch metrics."""
    
    # Parse and validate event body
    parsed_data = parse_event_body(event)
    symbols = parsed_data["symbols"]
    parameters = parsed_data["parameters"]
    
    logger.info(f"Processing request for symbols: {symbols}")
    
    # Initialize LunarCrush client
    api_key = os.getenv("LUNARCRUSH_API_KEY")
    if not api_key:
        raise ValueError("LUNARCRUSH_API_KEY environment variable is required")
    lunarcrush_client = LunarCrushClient(api_key)
    
    # Initialize S3 storage client (skip if endpoint is localhost and not available)
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")  # For LocalStack
    s3_storage = None
    
    # Only initialize S3 if we have a valid endpoint or it's not localhost
    if s3_endpoint_url and not "localhost" in s3_endpoint_url:
        try:
            s3_storage = S3Storage(
                bucket_name=s3_bucket_name,
                endpoint_url=s3_endpoint_url
            )
            logger.info("S3 storage initialized with custom endpoint")
        except Exception as e:
            logger.warning(f"Failed to initialize S3 storage: {e}")
            s3_storage = None
    elif not s3_endpoint_url:
        # Production AWS S3
        try:
            s3_storage = S3Storage(bucket_name=s3_bucket_name)
            logger.info("S3 storage initialized with AWS")
        except Exception as e:
            logger.warning(f"Failed to initialize S3 storage: {e}")
            s3_storage = None
    else:
        logger.info("Skipping S3 storage initialization for localhost endpoint")
    
    # Fetch comprehensive metrics (current + historical + changes)
    social_metrics = lunarcrush_client.get_comprehensive_metrics(symbols)
    
    # Store metrics in S3 if available
    if s3_storage and social_metrics:
        try:
            s3_storage.store_metrics(social_metrics)
            logger.info(f"Stored metrics for {len(social_metrics)} symbols in S3")
        except Exception as e:
            logger.warning(f"Failed to store metrics in S3: {e}")
    elif not s3_storage:
        logger.info("S3 storage not available, skipping storage")
    
    # Convert SocialMetrics objects to dictionaries for response
    metrics_data = []
    for metric in social_metrics:
        metrics_data.append(metric.to_dict())
    
    # Add metadata to response
    response_data = {
        "metrics": metrics_data,
        "metadata": {
            "symbols_requested": symbols,
            "count": len(social_metrics),
            "timestamp": None,  # Will be set when handler is called
            "s3_bucket": s3_bucket_name,
            "s3_file": "candidates.json"
        }
    }
    
    # Add any additional parameters to metadata
    if parameters:
        response_data["metadata"]["parameters"] = parameters
    
    logger.info(f"Successfully processed {len(social_metrics)} symbols")
    return response_data


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main AWS Lambda handler function.

    This function handles incoming Lambda events, processes cryptocurrency
    symbol requests, fetches metrics from the LunarCrush API, and returns
    properly formatted responses.

    Args:
        event: AWS Lambda event dictionary containing request data
        context: AWS Lambda context object (not used in this implementation)

    Returns:
        Dictionary formatted for AWS Lambda with statusCode, headers, and body

    Example Events:
        # API Gateway POST request:
        {
            "body": "{\\"symbols\\": [\\"BTC\\", \\"ETH\\"]}",
            "httpMethod": "POST",
            "headers": {...}
        }
        
        # Direct invocation:
        {
            "symbols": ["BTC", "ETH"]
        }
    """
    
    # Add timestamp for logging
    import time
    timestamp = int(time.time())
    
    # Log request details (with sensitive data masked)
    logger.info(
        "Lambda function invoked",
        extra={
            "request_id": getattr(context, "aws_request_id", "unknown"),
            "function_name": getattr(context, "function_name", "unknown"),
            "function_version": getattr(context, "function_version", "unknown"),
            "timestamp": timestamp
        }
    )
    
    return handle_api_errors(lambda_handler_inner)(event, context)


def lambda_handler_inner(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Inner lambda handler without error handling decorator."""
    # Add timestamp for logging
    import time
    timestamp = int(time.time())
    
    # Log request details (with sensitive data masked)
    logger.info(
        "Lambda function invoked",
        extra={
            "request_id": getattr(context, "aws_request_id", "unknown"),
            "function_name": getattr(context, "function_name", "unknown"),
            "function_version": getattr(context, "function_version", "unknown"),
            "timestamp": timestamp
        }
    )
    
    # Validate environment variables
    validate_environment()
    
    # Handle OPTIONS requests for CORS
    if event.get("httpMethod") == "OPTIONS":
        return LambdaResponse.success({}, 200)
    
    # Process the request
    response_data = process_symbols(event)
    
    # Update metadata with actual timestamp
    if response_data and isinstance(response_data, dict) and "metadata" in response_data:
        response_data["metadata"]["timestamp"] = timestamp
    
    # Check if response_data is valid before logging
    if response_data and isinstance(response_data, dict) and "metadata" in response_data:
        # Log successful completion
        logger.info(
            "Lambda function completed successfully",
            extra={
                "symbols_count": len(response_data["metadata"]["symbols_requested"]),
                "processing_time_ms": (int(time.time() * 1000) - int(timestamp * 1000))
            }
        )
    
    return LambdaResponse.success(response_data)


# For local testing
if __name__ == "__main__":
    # Test event for local development
    test_event = {
        "symbols": ["BTC", "ETH", "ADA"]
    }
    
    # Mock context object
    class MockContext:
        aws_request_id = "test-request-id"
        function_name = "test-function"
        function_version = "test-version"
    
    print("Testing lambda_handler locally...")
    result = lambda_handler(test_event, MockContext())
    print("Result:", json.dumps(result, indent=2))
