"""Base agent class."""

from abc import ABC
from backend.app.core.logging import logger


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    def log(self, message: str) -> None:
        logger.info(f"[{self.name}] {message}")
