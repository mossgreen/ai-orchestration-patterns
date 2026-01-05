"""
Base service interface for independent workflow services.
Each service can be deployed independently (e.g., as AWS Lambda).
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from ..models import ServiceResponse

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseService(ABC):
    """
    Abstract base class for independent services.

    Each service:
    - Has a single responsibility
    - Receives input, produces output (stateless)
    - Can be deployed independently
    - Returns ServiceResponse for consistent error handling
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Service identifier for logging."""
        pass

    @abstractmethod
    async def execute(self, request: dict[str, Any]) -> ServiceResponse:
        """
        Execute the service logic.

        Args:
            request: Service-specific input data

        Returns:
            ServiceResponse with success status and data/error
        """
        pass
