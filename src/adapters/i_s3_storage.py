"""
Interface for S3 storage operations.

This module defines the abstract interface for S3 storage operations,
following Clean Architecture principles where interfaces are defined
in the domain layer and implemented in the adapters layer.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.lunarcrush_client import SocialMetrics


class IS3Storage(ABC):
    """
    Abstract interface for S3 storage operations.

    This interface defines the contract for S3 storage implementations,
    providing methods to store and retrieve cryptocurrency metrics data.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve current metrics from S3.

        Returns:
            Current metrics data as dictionary, or None if not found

        Raises:
            Various storage-related exceptions
        """
        pass

    @abstractmethod
    def archive_current_file(self) -> str:
        """
        Archive the current metrics file with timestamp.

        Returns:
            Archive file name

        Raises:
            Various storage-related exceptions
        """
        pass

    @abstractmethod
    def list_archive_files(self) -> List[str]:
        """
        List all archived files in the bucket.

        Returns:
            List of archive file names

        Raises:
            Various storage-related exceptions
        """
        pass

    @abstractmethod
    def format_metrics_json(self, metrics: List[SocialMetrics]) -> Dict[str, Any]:
        """
        Format metrics data into the expected JSON structure.

        Args:
            metrics: List of SocialMetrics objects

        Returns:
            Formatted JSON structure for S3 storage
        """
        pass