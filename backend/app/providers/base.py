"""Abstract base class for all external providers with Zero-Cost gate."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.app.config import settings
from backend.app.core.logging import logger


class BaseProvider(ABC):
    """Base provider interface."""

    def __init__(self, name: str):
        self.name = name

    @property
    def is_zero_cost(self) -> bool:
        return True

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify API connectivity or local model availability."""
        pass
