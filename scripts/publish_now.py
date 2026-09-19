"""CLI Runner to generate and publish an Instagram Reel live immediately."""

import asyncio
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings
from backend.app.pipeline.orchestrator import create_default_orchestrator


async def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass

    niche = os.getenv("REEL_NICHE", getattr(settings, "niche", "python program quiz card reels"))
    topic = os.getenv("REEL_TOPIC", "")
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    if not topic:
        from backend.app.agents.idea import IdeaAgent
        idea_agent = IdeaAgent()
        ideas = await idea_agent.generate_ideas(niche=niche, count=3)
        if ideas and isinstance(ideas, list) and len(ideas) > 0:
            topic = ideas[0].get("topic", "Python Quiz: What is the output of print([1, 2] * 2)?")
        else:
            topic = "Python Quiz: What is the output of print([1, 2] * 2)?"

    print("=" * 60)
    print(f"🚀 AI Instagram Reels Autopilot — Runner")
    print(f"Target Account: {settings.effective_instagram_account_id}")
    print(f"Topic: {topic}")
    print(f"Niche: {niche}")
    print(f"Dry Run: {dry_run}")
    print("=" * 60)

    from backend.app.core.db import AsyncMongoDB
    await AsyncMongoDB.connect()

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
