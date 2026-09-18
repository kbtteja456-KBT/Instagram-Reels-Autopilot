"""Base Pydantic model with MongoDB serialization helpers."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MongoBaseModel(BaseModel):
    """Base model with datetime and MongoDB _id helpers."""
    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

    def to_mongo_dict(self) -> Dict[str, Any]:
        """Convert model to MongoDB document dict."""
        d = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in d and d["_id"] is None:
            del d["_id"]
        return d
