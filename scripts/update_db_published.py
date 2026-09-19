import asyncio
from backend.app.core.db import AsyncMongoDB

async def main():
    await AsyncMongoDB.connect()
    db = AsyncMongoDB.get_db()
    res = await db.reels.update_one(
        {"job_id": "e4c203a0-461"},
        {"$set": {
            "status": "PUBLISHED",
            "instagram_media_id": "17875653309632729",
            "instagram_url": "https://www.instagram.com/reel/Ddc7TUSEnp6/"
        }}
    )
    print("Updated:", res.modified_count)

if __name__ == "__main__":
    asyncio.run(main())
