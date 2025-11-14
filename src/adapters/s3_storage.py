"""
S3 storage implementation for cryptocurrency metrics data.

This module provides a concrete implementation of the S3 storage interface
using boto3 for AWS S3 operations, supporting both LocalStack and AWS S3.
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from urllib.parse import urlparse

import boto3
import structlog
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

from src.adapters.i_s3_storage import IS3Storage
from src.lunarcrush_client import SocialMetrics
from src.exceptions import (
    LunarCrushAPIError,
    LunarCrushNetworkError,
    LunarCrushDataValidationError
)

logger = structlog.get_logger(__name__)


class S3Storage(IS3Storage):
    """
    S3 storage implementation for cryptocurrency metrics data.

    This class provides methods to store and retrieve metrics data from S3,
    handling both local LocalStack and AWS S3 environments.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        aws_region: Optional[str] = None
    ):
        """
        Initialize S3 storage client.

        Args:
            bucket_name: S3 bucket name (if None, loads from environment)
            endpoint_url: S3 endpoint URL (for LocalStack or custom endpoints)
            aws_region: AWS region (if None, loads from environment)
        """
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")

        # Configure endpoint for LocalStack or AWS
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        self.aws_region = aws_region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        # Initialize S3 client
        try:
            s3_config = {
                "region_name": self.aws_region,
            }
            
            if self.endpoint_url:
                s3_config["endpoint_url"] = self.endpoint_url
                logger.info("Using custom S3 endpoint", endpoint_url=self.endpoint_url)
            else:
                logger.info("Using AWS S3", region=self.aws_region)

            self.s3_client = boto3.client("s3", **s3_config)
            
            # Test connection by listing buckets (or just the target bucket)
            self._test_connection()
            
            logger.info("S3 storage initialized", bucket_name=self.bucket_name)

        except NoCredentialsError as e:
            raise ValueError("AWS credentials not found. Please configure AWS credentials.")
        except ValueError as e:
            # Re-raise ValueError from _test_connection (e.g., bucket not found)
            raise
        except Exception as e:
            raise LunarCrushNetworkError(f"Failed to initialize S3 client: {str(e)}")

    def _test_connection(self) -> None:
        """Test S3 connection and bucket access."""
        try:
            # Test bucket access
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.debug("S3 bucket access confirmed", bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                raise ValueError(f"S3 bucket '{self.bucket_name}' does not exist")
            elif error_code == "403":
                raise ValueError(f"No access to S3 bucket '{self.bucket_name}'")
            else:
                raise LunarCrushNetworkError(f"S3 connection test failed: {str(e)}")

    def store_metrics(self, metrics: List[SocialMetrics]) -> bool:
        """
        Store social metrics data to S3.

        Args:
            metrics: List of SocialMetrics objects to store

        Returns:
            True if storage was successful, False otherwise

        Raises:
            Various storage-related exceptions
        """
        if not metrics:
            logger.warning("No metrics provided for storage")
            return False

        try:
            # Archive current file before storing new data
            try:
                self.archive_current_file()
            except Exception as e:
                logger.warning("Failed to archive current file", error=str(e))

            # Format metrics data
            formatted_data = self.format_metrics_json(metrics)
            
            # Store as candidates.json
            key = "candidates.json"
            
            # Convert to JSON string
            json_data = json.dumps(formatted_data, indent=2, default=str)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data.encode("utf-8"),
                ContentType="application/json",
                Metadata={
                    "symbols_count": str(len(metrics)),
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            )

            logger.info(
                "Metrics stored successfully",
                bucket=self.bucket_name,
                key=key,
                symbols_count=len(metrics)
            )
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(
                "S3 storage failed",
                error_code=error_code,
                error_message=error_message,
                bucket=self.bucket_name
            )
            raise LunarCrushNetworkError(f"S3 storage failed: {error_message}")

        except Exception as e:
            logger.error("Failed to store metrics", error=str(e), bucket=self.bucket_name)
            raise LunarCrushAPIError(f"Failed to store metrics: {str(e)}")

    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve current metrics from S3.

        Returns:
            Current metrics data as dictionary, or None if not found

        Raises:
            Various storage-related exceptions
        """
        try:
            key = "candidates.json"
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            # Read and parse JSON content
            content = response["Body"].read().decode("utf-8")
            metrics_data = json.loads(content)
            
            logger.debug(
                "Current metrics retrieved",
                bucket=self.bucket_name,
                key=key,
                content_length=len(content)
            )
            
            return metrics_data

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchKey":
                logger.info("No current metrics file found", bucket=self.bucket_name, key="candidates.json")
                return None
            else:
                logger.error(
                    "Failed to retrieve current metrics",
                    error_code=error_code,
                    error_message=e.response["Error"]["Message"],
                    bucket=self.bucket_name
                )
                raise LunarCrushNetworkError(f"Failed to retrieve current metrics: {error_code}")

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in current metrics file", error=str(e))
            raise LunarCrushDataValidationError(f"Invalid JSON in current metrics file: {str(e)}")

        except Exception as e:
            logger.error("Failed to get current metrics", error=str(e))
            raise LunarCrushAPIError(f"Failed to get current metrics: {str(e)}")

    def archive_current_file(self) -> str:
        """
        Archive the current metrics file with timestamp.

        Returns:
            Archive file name

        Raises:
            Various storage-related exceptions
        """
        try:
            current_key = "candidates.json"
            
            # Check if current file exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=current_key)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    logger.info("No current file to archive", key=current_key)
                    return ""
                raise

            # Generate archive filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            archive_key = f"archive/candidates_{timestamp}.json"
            
            # Copy current file to archive location
            copy_source = {
                "Bucket": self.bucket_name,
                "Key": current_key
            }
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=archive_key
            )
            
            logger.info(
                "Current file archived successfully",
                bucket=self.bucket_name,
                source_key=current_key,
                archive_key=archive_key
            )
            
            return archive_key

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(
                "Failed to archive current file",
                error_code=error_code,
                error_message=error_message,
                bucket=self.bucket_name
            )
            raise LunarCrushNetworkError(f"Failed to archive current file: {error_message}")

        except Exception as e:
            logger.error("Failed to archive current file", error=str(e))
            raise LunarCrushAPIError(f"Failed to archive current file: {str(e)}")

    def list_archive_files(self) -> List[str]:
        """
        List all archived files in the bucket.

        Returns:
            List of archive file names

        Raises:
            Various storage-related exceptions
        """
        try:
            prefix = "archive/"
            
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            archive_files = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        key = obj["Key"]
                        # Include only files, not subdirectories
                        if key != prefix and not key.endswith("/"):
                            archive_files.append(key)
            
            # Sort by filename (which includes timestamp)
            archive_files.sort(reverse=True)  # Most recent first
            
            logger.debug(
                "Archive files listed",
                bucket=self.bucket_name,
                file_count=len(archive_files)
            )
            
            return archive_files

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(
                "Failed to list archive files",
                error_code=error_code,
                error_message=error_message,
                bucket=self.bucket_name
            )
            raise LunarCrushNetworkError(f"Failed to list archive files: {error_message}")

        except Exception as e:
            logger.error("Failed to list archive files", error=str(e))
            raise LunarCrushAPIError(f"Failed to list archive files: {str(e)}")

    def format_metrics_json(self, metrics: List[SocialMetrics]) -> Dict[str, Any]:
        """
        Format metrics data into the expected JSON structure.

        Args:
            metrics: List of SocialMetrics objects

        Returns:
            Formatted JSON structure for S3 storage
        """
        try:
            formatted_metrics = []
            
            for metric in metrics:
                # Format each metric according to the Lambda function expectations
                formatted_metric = {
                    "symbol": metric.symbol,
                    "current": {
                        "interactions_24h": metric.current_metrics.interactions_24h,
                        "social_volume_24h": metric.current_metrics.social_volume_24h,
                        "social_dominance": metric.current_metrics.social_dominance,
                        "galaxy_score": metric.current_metrics.galaxy_score,
                        "galaxy_score_previous": metric.current_metrics.galaxy_score_previous,
                        "sentiment": metric.current_metrics.sentiment,
                        "alt_rank": metric.current_metrics.alt_rank,
                        "alt_rank_previous": metric.current_metrics.alt_rank_previous
                    },
                    "changes": {
                        "interactions_24h_pct": metric.momentum_metrics.interactions_trend,
                        "social_volume_24h_pct": metric.momentum_metrics.volume_trend,
                        "social_dominance_pct": metric.momentum_metrics.social_dominance_trend,
                        "galaxy_score_change": metric.momentum_metrics.galaxy_score_trend,
                        "sentiment_pct": metric.momentum_metrics.sentiment_trend,
                        "alt_rank_change": metric.momentum_metrics.alt_rank_trend
                    },
                    "timestamp": metric.timestamp.isoformat()
                }
                
                formatted_metrics.append(formatted_metric)
            
            # Create the final JSON structure
            result = {
                "metrics": formatted_metrics,
                "metadata": {
                    "count": len(formatted_metrics),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "symbols": [metric.symbol for metric in metrics]
                }
            }
            
            logger.debug(
                "Metrics formatted for JSON storage",
                symbols_count=len(metrics),
                output_structure="candidates.json format"
            )
            
            return result

        except Exception as e:
            logger.error("Failed to format metrics for JSON", error=str(e))
            raise LunarCrushDataValidationError(f"Failed to format metrics for JSON: {str(e)}")