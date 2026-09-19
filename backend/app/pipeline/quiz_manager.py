"""Quiz Manager: Tracks posted quizzes to prevent duplicates and provides fresh Python quizzes."""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.db import AsyncMongoDB


POSTED_FILE = Path(settings.media_storage_dir) / "posted_quizzes.json"

# Curated bank of viral, tricky Python gotcha quizzes
CURATED_QUIZZES = [
    {
        "quiz_id": "set_comprehension_modulo",
        "title": "Python Quiz: Set Comprehension & Sorting",
        "question": "What is the output of this code?",
        "file_tab": "main.py",
        "code": "s = {x % 3 for x in range(6)}\nprint(sorted(list(s)))",
        "badge_text": "Think carefully!",
        "options": [
            {"letter": "A", "text": "[0, 1, 2]"},
            {"letter": "B", "text": "[0, 1, 2, 0, 1, 2]"},
            {"letter": "C", "text": "[0, 1, 2, 3, 4, 5]"},
            {"letter": "D", "text": "{0, 1, 2}"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- Set {x % 3} eliminates duplicates, leaving: {0, 1, 2}",
            "- sorted(list(s)) returns the sorted list: [0, 1, 2]"
        ],
        "narration": (
            "What is the output of this tricky Python code? "
            "We have s equals {x modulo 3 for x in range 6}, then print sorted list of s. "
            "Which option is correct: A, B, C, or D? "
            "Pause the video and drop your answer in the comments right now! "
            "Three... two... one... "
            "The correct answer is Option A! "
            "The set eliminates duplicate remainders, leaving only zero, one, and two. "
            "Then sorted() converts it into an ordered list: bracket 0, 1, 2! "
            "Did you get it right? Save this Reel and follow for daily Python coding quizzes!"
        ),
        "caption": (
            "🔥 Python Quiz: What is the output of this code?\n\n"
            "```python\n"
            "s = {x % 3 for x in range(6)}\n"
            "print(sorted(list(s)))\n"
            "```\n\n"
            "Comment your answer before the reveal! 👇\n"
            "Option A: [0, 1, 2]\n"
            "Option B: [0, 1, 2, 0, 1, 2]\n"
            "Option C: [0, 1, 2, 3, 4, 5]\n"
            "Option D: {0, 1, 2}\n\n"
            "💡 Explanation: The set comprehension removes duplicates, leaving {0, 1, 2}. sorted() then returns the ordered list [0, 1, 2]!\n\n"
            "👉 Follow for daily Python & coding challenges!\n"
            "#python #coding #programming #developer #pythonquiz #softwareengineer #tech #computerscience #learnpython #code"
        )
    },
    {
        "quiz_id": "mutable_default_argument",
        "title": "Python Gotcha: Mutable Default Arguments",
        "question": "What is the output of this code?",
        "file_tab": "gotcha.py",
        "code": "def add(val, lst=[]):\n    lst.append(val)\n    return lst\n\nprint(add(1), add(2))",
        "badge_text": "Tricky gotcha!",
        "options": [
            {"letter": "A", "text": "[1] [2]"},
            {"letter": "B", "text": "[1] [1, 2]"},
            {"letter": "C", "text": "[1, 2] [1, 2]"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 1,  # Option B: [1] [1, 2]
        "explanation_lines": [
            "- In Python, default arguments evaluate once at definition!",
            "- The list persists across calls: [1] and [1, 2]"
        ],
        "narration": (
            "What is the output of this classic Python gotcha? "
            "We have def add of val with default empty list, then print add(1) and add(2). "
            "Is the answer Option A, B, C, or Option D? "
            "Pause the video and comment your answer below! "
            "Three... two... one... "
            "The correct answer is Option B: bracket 1, and bracket 1, 2! "
            "In Python, default arguments are only evaluated once when the function is defined. "
            "The same list is reused on subsequent calls! "
            "Did you get it right? Save this Reel and follow for daily Python quizzes!"
        ),
        "caption": (
            "🔥 Python Gotcha: What is the output of this code?\n\n"
            "```python\n"
            "def add(val, lst=[]):\n"
            "    lst.append(val)\n"
            "    return lst\n\n"
            "print(add(1), add(2))\n"
            "```\n\n"
            "Comment your answer before the reveal! 👇\n"
            "Option A: [1] [2]\n"
            "Option B: [1] [1, 2]\n"
            "Option C: [1, 2] [1, 2]\n"
            "Option D: TypeError\n\n"
            "💡 Explanation: Default arguments in Python evaluate only once when the function is defined, NOT on every call. The mutable list persists across calls!\n\n"
            "👉 Save & follow for daily Python gotchas!\n"
            "#python #coding #programming #developer #pythonquiz #pythonprogramming #tech #softwareengineer #coder"
        )
    },
    {
        "quiz_id": "is_vs_equality_slicing",
        "title": "Python Quiz: 'is' vs '==' Identity Trap",
        "question": "What is the output of this code?",
        "file_tab": "identity.py",
        "code": "a = [1, 2, 3]\nb = a[:]\nprint(a == b, a is b)",
        "badge_text": "Identity vs Value!",
        "options": [
            {"letter": "A", "text": "True True"},
            {"letter": "B", "text": "True False"},
            {"letter": "C", "text": "False True"},
            {"letter": "D", "text": "False False"}
        ],
        "correct_idx": 1,  # Option B: True False
        "explanation_lines": [
            "- '==' checks value equality: both lists have [1, 2, 3]",
            "- 'is' checks memory identity: slicing creates a new copy"
        ],
        "narration": (
            "Do you know the difference between is and double equals in Python? "
            "We have a equals [1, 2, 3] and b equals a slice. "
            "What does print(a == b, a is b) output? "
            "Option A, Option B, Option C, or Option D? "
            "Pause the video and drop your guess in the comments! "
            "Three... two... one... "
            "The correct answer is Option B: True False! "
            "Double equals checks value equality, which is True. "
            "But is checks if they share the exact same memory address. Slicing creates a new object in memory, so a is b is False! "
            "Save this Reel and follow for daily Python quizzes!"
        ),
        "caption": (
            "🔥 Python Quiz: What is the output of this code?\n\n"
            "```python\n"
            "a = [1, 2, 3]\n"
            "b = a[:]\n"
            "print(a == b, a is b)\n"
            "```\n\n"
            "Comment your answer! 👇\n"
            "Option A: True True\n"
            "Option B: True False\n"
            "Option C: False True\n"
            "Option D: False False\n\n"
            "💡 Explanation: '==' checks for value equality (True), while 'is' checks object identity (memory reference). Slicing creates a shallow copy, so 'a is b' is False!\n\n"
            "👉 Follow for daily Python quizzes!\n"
            "#python #coding #programming #developer #pythonquiz #computerscience #softwareengineer #tech"
        )
    },
    {
        "quiz_id": "bool_int_dict_key",
        "title": "Python Gotcha: Boolean Dictionary Keys",
        "question": "What is the output of this code?",
        "file_tab": "keys.py",
        "code": "d = {1: 'one', True: 'true'}\nprint(len(d), d[1])",
        "badge_text": "bool is int subclass!",
        "options": [
            {"letter": "A", "text": "2 'one'"},
            {"letter": "B", "text": "1 'true'"},
            {"letter": "C", "text": "2 'true'"},
            {"letter": "D", "text": "1 'one'"}
        ],
        "correct_idx": 1,  # Option B: 1 'true'
        "explanation_lines": [
            "- In Python, bool is a subclass of int: True == 1 and hash(True) == hash(1)",
            "- True overwrites key 1, resulting in length 1 and value 'true'"
        ],
        "narration": (
            "Can you solve this surprising Python dictionary riddle? "
            "d equals curly bracket 1 colon 'one', True colon 'true'. "
            "What does print(len(d), d[1]) output? "
            "Option A, Option B, Option C, or Option D? "
            "Pause and comment your answer right now! "
            "Three... two... one... "
            "The correct answer is Option B: 1 'true'! "
            "In Python, bool is a subclass of int. True equals 1 and produces the exact same hash. "
            "So True overwrites key 1 in the dictionary! "
            "Did this trick you? Save this Reel and follow for daily Python quizzes!"
        ),
        "caption": (
            "🔥 Python Gotcha: What is the output of this code?\n\n"
            "```python\n"
            "d = {1: 'one', True: 'true'}\n"
            "print(len(d), d[1])\n"
            "```\n\n"
            "Comment your answer before the reveal! 👇\n"
            "Option A: 2 'one'\n"
            "Option B: 1 'true'\n"
            "Option C: 2 'true'\n"
            "Option D: 1 'one'\n\n"
            "💡 Explanation: In Python, bool is a subclass of int! True == 1 and hash(True) == hash(1). Therefore, key True overwrites 1!\n\n"
            "👉 Save & follow for daily Python challenges!\n"
            "#python #coding #programming #developer #pythonquiz #softwareengineer #tech"
        )
    }
]


class QuizManager:
    """Manages deduplication and provides never-before-posted quizzes."""

    def __init__(self):
        POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.posted_file = POSTED_FILE
        self._ensure_initial_posted_state()

    def _ensure_initial_posted_state(self):
        """Seed the first reel we just published into the posted registry."""
        posted = self.get_posted_quiz_ids()
        # Ensure our first published reel is marked as posted
        if "set_comprehension_modulo" not in posted:
            self.record_posted_quiz(
                quiz_id="set_comprehension_modulo",
                title="Python Quiz: Set Comprehension & Sorting",
                media_id="18061233950716294",
                instagram_url="https://www.instagram.com/reel/DddT8CnEttO/"
            )

    def get_posted_quiz_ids(self) -> List[str]:
        """Return list of all quiz_ids that have already been posted."""
        if self.posted_file.exists():
            try:
                with open(self.posted_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [item.get("quiz_id") for item in data if "quiz_id" in item]
            except Exception as e:
                logger.warning(f"[QuizManager] Read error: {e}")
        return []

    def is_posted(self, quiz_id: str) -> bool:
        """Check if a quiz has already been posted to Instagram."""
        return quiz_id in self.get_posted_quiz_ids()

    def record_posted_quiz(
        self,
        quiz_id: str,
        title: str,
        media_id: str,
        instagram_url: str,
        file_path: Optional[str] = None
    ) -> None:
        """Record a posted quiz to prevent it from ever being posted again."""
        posted_data = []
        if self.posted_file.exists():
            try:
                with open(self.posted_file, "r", encoding="utf-8") as f:
                    posted_data = json.load(f)
            except Exception:
                posted_data = []

        # Avoid duplicate entries in local history
        if any(item.get("quiz_id") == quiz_id for item in posted_data):
            return

        record = {
            "quiz_id": quiz_id,
            "title": title,
            "media_id": media_id,
            "instagram_url": instagram_url,
            "file_path": file_path,
            "posted_at": datetime.now(timezone.utc).isoformat()
        }
        posted_data.append(record)

        with open(self.posted_file, "w", encoding="utf-8") as f:
            json.dump(posted_data, f, indent=2)

        logger.info(f"[QuizManager] Registered posted quiz '{quiz_id}' to prevent duplicates.")

    def get_next_unposted_quiz(self) -> Dict[str, Any]:
        """Find the next fresh, never-posted quiz."""
        posted_ids = self.get_posted_quiz_ids()
        logger.info(f"[QuizManager] Already posted quizzes: {posted_ids}")

        for quiz in CURATED_QUIZZES:
            if quiz["quiz_id"] not in posted_ids:
                logger.info(f"[QuizManager] Selected fresh unposted quiz: '{quiz['quiz_id']}' - {quiz['title']}")
                return quiz

        # If all curated quizzes posted, generate a fresh unique one
        raise RuntimeError("All curated quizzes have been posted! Add more quizzes to the bank or enable AI generation.")
