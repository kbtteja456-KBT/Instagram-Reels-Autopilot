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
    },
    {
        "quiz_id": "tuple_mutation_gotcha",
        "title": "Python Gotcha: Mutating List inside Tuple",
        "question": "What is the output of this code?",
        "file_tab": "tuple_bug.py",
        "code": "t = (1, 2, [3, 4])\ntry:\n    t[2] += [5]\nexcept TypeError:\n    pass\nprint(t[2])",
        "badge_text": "Tuple Gotcha!",
        "options": [
            {"letter": "A", "text": "[3, 4]"},
            {"letter": "B", "text": "[3, 4, 5]"},
            {"letter": "C", "text": "TypeError"},
            {"letter": "D", "text": "None"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- '+=' modifies list in-place BEFORE tuple assignment fails!",
            "- The list gets [5] appended despite the TypeError exception"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: What is the output of this code?\n\n```python\nt = (1, 2, [3, 4])\ntry:\n    t[2] += [5]\nexcept TypeError:\n    pass\nprint(t[2])\n```\n\nComment your guess before time runs out! 👇\nOption A: [3, 4]\nOption B: [3, 4, 5]\nOption C: TypeError\nOption D: None\n\n💡 Explanation: In Python, '+=' extends the inner list in-place first, then attempts to assign back to the tuple which raises TypeError! So [5] is added!\n\n👉 Follow for daily Python quizzes!\n#python #coding #programming #developer #pythonquiz"
    },
    {
        "quiz_id": "string_step_slicing",
        "title": "Python Quiz: Negative Step String Slicing",
        "question": "What is the output of this code?",
        "file_tab": "slicing.py",
        "code": "s = 'PYTHON'\nprint(s[::-2])",
        "badge_text": "String Slicing!",
        "options": [
            {"letter": "A", "text": "'NTP'"},
            {"letter": "B", "text": "'NHY'"},
            {"letter": "C", "text": "'PYT'"},
            {"letter": "D", "text": "'NOT'"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- Step '-2' traverses backwards from end taking every 2nd char",
            "- 'PYTHON': indices 5('N'), 3('T'), 1('P') -> 'NTP'"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: What is the output of this code?\n\n```python\ns = 'PYTHON'\nprint(s[::-2])\n```\n\nComment your answer before the reveal! 👇\nOption A: 'NTP'\nOption B: 'NHY'\nOption C: 'PYT'\nOption D: 'NOT'\n\n💡 Explanation: The slice [::-2] starts from the last character 'N' and steps backwards by 2: 'N', then 'T', then 'P' -> 'NTP'!\n\n👉 Save & follow for daily quizzes!\n#python #coding #programming #developer #quiz"
    },
    {
        "quiz_id": "generator_exhaustion",
        "title": "Python Gotcha: Generator Exhaustion",
        "question": "What is the output of this code?",
        "file_tab": "gen.py",
        "code": "g = (x * 2 for x in range(3))\nprint(list(g), list(g))",
        "badge_text": "Generators!",
        "options": [
            {"letter": "A", "text": "[0, 2, 4] [0, 2, 4]"},
            {"letter": "B", "text": "[0, 2, 4] []"},
            {"letter": "C", "text": "[] []"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- Generators can only be consumed once!",
            "- Second list(g) call returns empty list []"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: What is the output of this code?\n\n```python\ng = (x * 2 for x in range(3))\nprint(list(g), list(g))\n```\n\nDrop your guess! 👇\nOption A: [0, 2, 4] [0, 2, 4]\nOption B: [0, 2, 4] []\nOption C: [] []\nOption D: TypeError\n\n💡 Explanation: Python generators are one-time iterators. After the first list(g) consumes all values, subsequent iterations yield empty []!\n\n👉 Follow for daily Python quizzes!\n#python #coding #programming #developer #pythonquiz"
    },
    {
        "quiz_id": "all_any_empty_list",
        "title": "Python Trap: all([]) and any([])",
        "question": "What is the output of this code?",
        "file_tab": "truthy.py",
        "code": "print(all([]), any([]))",
        "badge_text": "Vacuous Truth!",
        "options": [
            {"letter": "A", "text": "True False"},
            {"letter": "B", "text": "False False"},
            {"letter": "C", "text": "True True"},
            {"letter": "D", "text": "False True"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- all([]) is True (vacuous truth: no element is falsy)",
            "- any([]) is False (no element is truthy)"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: What is the output of this code?\n\n```python\nprint(all([]), any([]))\n```\n\nCan you get this right? 👇\nOption A: True False\nOption B: False False\nOption C: True True\nOption D: False True\n\n💡 Explanation: all([]) returns True (vacuously true because no item is False), while any([]) returns False because no item is True!\n\n👉 Follow for daily Python quizzes!\n#python #coding #developer #quiz"
    },
    {
        "quiz_id": "integer_interning_256",
        "title": "Python Trap: Integer Caching / Interning",
        "question": "What is the output of this code?",
        "file_tab": "intern.py",
        "code": "x = 256\ny = 256\nprint(x is y)",
        "badge_text": "Memory Interning!",
        "options": [
            {"letter": "A", "text": "True"},
            {"letter": "B", "text": "False"},
            {"letter": "C", "text": "TypeError"},
            {"letter": "D", "text": "None"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- CPython pre-allocates small integers from -5 to 256",
            "- Both x and y point to the exact same memory object"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: What is the output of this code?\n\n```python\nx = 256\ny = 256\nprint(x is y)\n```\n\nOption A: True\nOption B: False\nOption C: TypeError\nOption D: None\n\n💡 Explanation: CPython caches small integers between -5 and 256, so x is y evaluates to True! (Values > 256 allocate new objects!)\n\n👉 Follow for daily Python quizzes!\n#python #coding #programming #developer"
    },
    {
        "quiz_id": "list_multiplication_reference",
        "title": "Python Gotcha: Nested List Multiplication",
        "question": "What is the output of this code?",
        "file_tab": "nested.py",
        "code": "grid = [[0]] * 2\ngrid[0][0] = 1\nprint(grid[1][0])",
        "badge_text": "Reference Trap!",
        "options": [
            {"letter": "A", "text": "0"},
            {"letter": "B", "text": "1"},
            {"letter": "C", "text": "[[1]]"},
            {"letter": "D", "text": "IndexError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- '*' copies inner list references, not copies of data!",
            "- Modifying grid[0] modifies the same inner list in grid[1]"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: What is the output of this code?\n\n```python\ngrid = [[0]] * 2\ngrid[0][0] = 1\nprint(grid[1][0])\n```\n\nComment your answer! 👇\nOption A: 0\nOption B: 1\nOption C: [[1]]\nOption D: IndexError\n\n💡 Explanation: Multiplying a list containing a list copies the reference, NOT the list. Both rows point to the exact same object, so grid[1][0] is 1!\n\n👉 Follow for daily quizzes!\n#python #coding #developer #quiz"
    },
    {
        "quiz_id": "dict_get_default_val",
        "title": "Python Quiz: dict.get() with None",
        "question": "What is the output of this code?",
        "file_tab": "dict_get.py",
        "code": "d = {'a': None}\nprint(d.get('a', 1), d.get('b', 1))",
        "badge_text": "dict.get Gotcha!",
        "options": [
            {"letter": "A", "text": "None 1"},
            {"letter": "B", "text": "1 1"},
            {"letter": "C", "text": "None None"},
            {"letter": "D", "text": "KeyError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- 'a' exists in d with value None, so get('a', 1) returns None",
            "- 'b' does NOT exist, so get('b', 1) returns default 1"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: What is the output of this code?\n\n```python\nd = {'a': None}\nprint(d.get('a', 1), d.get('b', 1))\n```\n\nComment your guess! 👇\nOption A: None 1\nOption B: 1 1\nOption C: None None\nOption D: KeyError\n\n💡 Explanation: dict.get(key, default) only returns the default if key is MISSING from dictionary! Since 'a' is present, it returns None!\n\n👉 Follow for daily Python quizzes!\n#python #coding #programming"
    },
    {
        "quiz_id": "finally_return_override",
        "title": "Python Trap: finally Block Return Override",
        "question": "What is the output of this code?",
        "file_tab": "try_finally.py",
        "code": "def func():\n    try:\n        return 1\n    finally:\n        return 2\n\nprint(func())",
        "badge_text": "finally overrides!",
        "options": [
            {"letter": "A", "text": "1"},
            {"letter": "B", "text": "2"},
            {"letter": "C", "text": "3"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- finally blocks ALWAYS execute before returning",
            "- A return in finally overrides any return in try!"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: What is the output of this code?\n\n```python\ndef func():\n    try:\n        return 1\n    finally:\n        return 2\n\nprint(func())\n```\n\nCan you solve this? 👇\nOption A: 1\nOption B: 2\nOption C: 3\nOption D: TypeError\n\n💡 Explanation: A return statement inside a finally block takes precedence and overrides any return or exception raised in the try block!\n\n👉 Follow for daily Python quizzes!\n#python #coding #developer #quiz"
    },
    {
        "quiz_id": "float_precision_03",
        "title": "Python Quiz: Floating Point Precision",
        "question": "What is the output of this code?",
        "file_tab": "floats.py",
        "code": "print(0.1 + 0.2 == 0.3)",
        "badge_text": "IEEE 754 Floats!",
        "options": [
            {"letter": "A", "text": "True"},
            {"letter": "B", "text": "False"},
            {"letter": "C", "text": "0.30000000000000004"},
            {"letter": "D", "text": "SyntaxError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- 0.1 + 0.2 evaluates to 0.30000000000000004 in binary float",
            "- So 0.1 + 0.2 == 0.3 evaluates to False!"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: What is the output of this code?\n\n```python\nprint(0.1 + 0.2 == 0.3)\n```\n\nTrue or False? 👇\nOption A: True\nOption B: False\nOption C: 0.30000000000000004\nOption D: SyntaxError\n\n💡 Explanation: Due to IEEE 754 binary floating-point representation, 0.1 + 0.2 is actually 0.30000000000000004, so equality with 0.3 is False!\n\n👉 Follow for daily quizzes!\n#python #coding #programming #developer"
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
        """Return list of all quiz_ids that have already been posted (from local cache and MongoDB Atlas)."""
        posted_ids = set()

        # 1. Local JSON file
        if self.posted_file.exists():
            try:
                with open(self.posted_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        if item.get("quiz_id"):
                            posted_ids.add(item["quiz_id"])
            except Exception as e:
                logger.warning(f"[QuizManager] Local read error: {e}")

        # 2. MongoDB Atlas Cloud database (cross-machine / GitHub Actions runner sync)
        try:
            from pymongo import MongoClient
            from backend.app.config import settings
            if settings.mongodb_uri and not settings.mongodb_uri.startswith("mock"):
                client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
                db = client[settings.mongodb_db_name]
                
                # Check posted_quizzes collection
                for doc in db.posted_quizzes.find({}, {"quiz_id": 1}):
                    if doc.get("quiz_id"):
                        posted_ids.add(doc["quiz_id"])

                # Check reels collection by title matching
                title_to_id = {q["title"].lower(): q["quiz_id"] for q in CURATED_QUIZZES}
                for doc in db.reels.find({"status": "PUBLISHED"}, {"title": 1}):
                    t = (doc.get("title") or "").lower()
                    if t in title_to_id:
                        posted_ids.add(title_to_id[t])
                    for q in CURATED_QUIZZES:
                        if q["quiz_id"] in t or any(k in t for k in q["quiz_id"].split("_")):
                            posted_ids.add(q["quiz_id"])
        except Exception as e:
            logger.warning(f"[QuizManager] MongoDB sync note: {e}")

        return list(posted_ids)

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
        """Record a posted quiz in both local cache and MongoDB Atlas to prevent duplicates."""
        posted_data = []
        if self.posted_file.exists():
            try:
                with open(self.posted_file, "r", encoding="utf-8") as f:
                    posted_data = json.load(f)
            except Exception:
                posted_data = []

        if not any(item.get("quiz_id") == quiz_id for item in posted_data):
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

        # Sync to MongoDB Atlas cloud database
        try:
            from pymongo import MongoClient
            from backend.app.config import settings
            if settings.mongodb_uri and not settings.mongodb_uri.startswith("mock"):
                client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
                db = client[settings.mongodb_db_name]
                db.posted_quizzes.update_one(
                    {"quiz_id": quiz_id},
                    {"$set": {
                        "quiz_id": quiz_id,
                        "title": title,
                        "media_id": str(media_id),
                        "instagram_url": str(instagram_url),
                        "posted_at": datetime.now(timezone.utc).isoformat()
                    }},
                    upsert=True
                )
        except Exception as e:
            logger.warning(f"[QuizManager] MongoDB write note: {e}")

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
