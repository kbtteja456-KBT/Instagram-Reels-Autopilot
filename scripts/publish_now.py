"""CLI Runner to generate and publish an Instagram Reel live immediately."""

import asyncio
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings
from backend.app.pipeline.orchestrator import create_default_orchestrator


async def main():
    topic = os.getenv("REEL_TOPIC", "3 High-Performance Habits of Successful Creators")
    niche = os.getenv("REEL_NICHE", "Motivation & Success")
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    print("=" * 60)
    print(f"🚀 AI Instagram Reels Autopilot — Runner")
    print(f"Target Account: {settings.effective_instagram_account_id}")
    print(f"Topic: {topic}")
    print(f"Niche: {niche}")
    print(f"Dry Run: {dry_run}")
    print("=" * 60)

    orchestrator = create_default_orchestrator()
    result = await orchestrator.execute_full_flow(
        topic=topic,
        niche=niche,
        publish_immediately=True,
        dry_run=dry_run
    )

    print("\n" + "=" * 60)
    print("🎉 Pipeline Run Finished!")
    print(f"Status: {result.get('status')}")
    print(f"Title: {result.get('title')}")
    print(f"Quality Score: {result.get('quality_score')}")
    if result.get("instagram_url"):
        print(f"Instagram URL: {result.get('instagram_url')}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
