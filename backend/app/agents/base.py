"""Base agent class."""

from abc import ABC
from backend.app.core.logging import logger


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    def log(self, message: str, level: str = "INFO") -> None:
        lvl = level.upper()
        if lvl == "WARNING":
            logger.warning(f"[{self.name}] {message}")
        elif lvl == "ERROR":
            logger.error(f"[{self.name}] {message}")
        elif lvl == "DEBUG":
            logger.debug(f"[{self.name}] {message}")
        else:
            logger.info(f"[{self.name}] {message}")
