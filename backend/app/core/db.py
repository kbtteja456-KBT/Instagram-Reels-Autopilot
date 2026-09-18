"""MongoDB connection managers for both asynchronous (motor) and synchronous (pymongo) operations."""

from typing import Optional, Any
import motor.motor_asyncio
import pymongo
from pymongo.database import Database as SyncDatabase
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.config import settings
from backend.app.core.logging import logger


class AsyncMongoDB:
    """Asynchronous MongoDB manager using Motor."""
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        try:
            cls.client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=3000
            )
            cls.db = cls.client[settings.mongodb_db_name]
            # Ping to verify connection
            await cls.client.admin.command('ping')
            logger.info(f"[AsyncMongoDB] Successfully connected to {settings.mongodb_db_name}")
        except Exception as e:
            logger.warning(f"[AsyncMongoDB] MongoDB connection failed or offline ({e}). Operating in memory/mock fallback mode.")
            cls.client = None
            cls.db = None

    @classmethod
    async def disconnect(cls) -> None:
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("[AsyncMongoDB] Disconnected from MongoDB.")

    @classmethod
    def get_db(cls) -> Any:
        return cls.db


class SyncMongoDB:
    """Synchronous MongoDB manager using PyMongo."""
    _client: Optional[pymongo.MongoClient] = None
    _db: Optional[SyncDatabase] = None

    @classmethod
    def get_client(cls) -> Optional[pymongo.MongoClient]:
        if cls._client is None:
            try:
                cls._client = pymongo.MongoClient(
                    settings.mongodb_uri,
                    serverSelectionTimeoutMS=3000
                )
                cls._client.admin.command('ping')
            except Exception as e:
                logger.warning(f"[SyncMongoDB] MongoDB connection failed or offline ({e}).")
                cls._client = None
        return cls._client

    @classmethod
    def get_db(cls) -> Any:
        client = cls.get_client()
        if client:
            return client[settings.mongodb_db_name]
        return None
