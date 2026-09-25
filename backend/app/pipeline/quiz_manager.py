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
    },
    {
        "quiz_id": "bool_is_subclass_int",
        "title": "Python Quiz: bool as int Subclass",
        "question": "What is the output of this code?",
        "file_tab": "bool_math.py",
        "code": "print(True + True * False)",
        "badge_text": "Math with booleans!",
        "options": [
            {"letter": "A", "text": "0"},
            {"letter": "B", "text": "1"},
            {"letter": "C", "text": "2"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- In Python, bool is a subclass of int: True==1, False==0",
            "- Multiplication happens first: True * False = 1 * 0 = 0",
            "- Then addition: 1 + 0 = 1!"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: What is the output of this code?\n\n```python\nprint(True + True * False)\n```\n\nComment your answer! 👇\nOption A: 0\nOption B: 1\nOption C: 2\nOption D: TypeError\n\n💡 Explanation: In Python, bool inherits from int (True=1, False=0). Precedence rules apply: True * False is 0, so 1 + 0 = 1!\n\n👉 Follow for daily Python quizzes!\n#python #coding #softwareengineer"
    },
    {
        "quiz_id": "chained_comparison_trap",
        "title": "Python Quiz: Chained Comparison",
        "question": "What is the output of this code?",
        "file_tab": "chained.py",
        "code": "print(False == False in [False])",
        "badge_text": "Operator chaining!",
        "options": [
            {"letter": "A", "text": "True"},
            {"letter": "B", "text": "False"},
            {"letter": "C", "text": "TypeError"},
            {"letter": "D", "text": "[False]"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- Python chains comparison operators automatically!",
            "- (False == False in [False]) expands to:",
            "- (False == False) and (False in [False]) -> True and True = True!"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Chained comparison gotcha!\n\n```python\nprint(False == False in [False])\n```\n\nWhat will print? 👇\nOption A: True\nOption B: False\nOption C: TypeError\nOption D: [False]\n\n💡 Explanation: Comparison chaining transforms this into (False == False) and (False in [False]), which evaluates to True and True -> True!\n\n👉 Follow for daily coding challenges!\n#python #learnprogramming #code"
    },
    {
        "quiz_id": "string_split_none_whitespace",
        "title": "Python Quiz: str.split() vs str.split(' ')",
        "question": "What is the output of this code?",
        "file_tab": "splits.py",
        "code": "s = 'a   b'\nprint(len(s.split()), len(s.split(' ')))",
        "badge_text": "Subtle difference!",
        "options": [
            {"letter": "A", "text": "2 2"},
            {"letter": "B", "text": "2 4"},
            {"letter": "C", "text": "4 4"},
            {"letter": "D", "text": "2 5"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- s.split() groups consecutive whitespace: ['a', 'b'] (len 2)",
            "- s.split(' ') splits on every single space: ['a', '', '', 'b'] (len 4)!"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: split() vs split(' ')\n\n```python\ns = 'a   b'\nprint(len(s.split()), len(s.split(' ')))\n```\n\nCan you get this right? 👇\nOption A: 2 2\nOption B: 2 4\nOption C: 4 4\nOption D: 2 5\n\n💡 Explanation: .split() treats consecutive whitespace as one delimiter, while .split(' ') splits strictly on single spaces preserving empty strings!\n\n👉 Follow for daily Python tips!\n#python #developer #tech"
    },
    {
        "quiz_id": "dict_fromkeys_shared_list",
        "title": "Python Gotcha: dict.fromkeys() Shared Ref",
        "question": "What is the output of this code?",
        "file_tab": "fromkeys.py",
        "code": "d = dict.fromkeys(['a', 'b'], [])\nd['a'].append(1)\nprint(d)",
        "badge_text": "Classic mutability trap!",
        "options": [
            {"letter": "A", "text": "{'a': [1], 'b': []}"},
            {"letter": "B", "text": "{'a': [1], 'b': [1]}"},
            {"letter": "C", "text": "{'a': [], 'b': []}"},
            {"letter": "D", "text": "KeyError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- dict.fromkeys reuses the SAME instance for all keys!",
            "- Both 'a' and 'b' reference the exact same list object in memory",
            "- Modifying d['a'] modifies d['b'] as well!"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: dict.fromkeys() shared list trap!\n\n```python\nd = dict.fromkeys(['a', 'b'], [])\nd['a'].append(1)\nprint(d)\n```\n\nWhat is printed? 👇\nOption A: {'a': [1], 'b': []}\nOption B: {'a': [1], 'b': [1]}\nOption C: {'a': [], 'b': []}\nOption D: KeyError\n\n💡 Explanation: dict.fromkeys uses the identical object instance for every key. Both keys point to the exact same list in memory!\n\n👉 Follow for daily developer gotchas!\n#python #coding #programming"
    },
    {
        "quiz_id": "lambda_late_binding_closure",
        "title": "Python Quiz: Lambda Late Binding",
        "question": "What is the output of this code?",
        "file_tab": "lambdas.py",
        "code": "funcs = [lambda: i for i in range(3)]\nprint([f() for f in funcs])",
        "badge_text": "Tricky closures!",
        "options": [
            {"letter": "A", "text": "[0, 1, 2]"},
            {"letter": "B", "text": "[2, 2, 2]"},
            {"letter": "C", "text": "[3, 3, 3]"},
            {"letter": "D", "text": "NameError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- Python closures use late binding for variable lookup",
            "- 'i' is looked up when the lambda is CALLED, not when created",
            "- After the loop completes, i is 2, so all lambdas return 2!"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: Lambda closure late binding!\n\n```python\nfuncs = [lambda: i for i in range(3)]\nprint([f() for f in funcs])\n```\n\nWhat is the output? 👇\nOption A: [0, 1, 2]\nOption B: [2, 2, 2]\nOption C: [3, 3, 3]\nOption D: NameError\n\n💡 Explanation: Python closures bind variables late (at call time). When funcs are executed, the loop has ended and i holds 2 for all of them!\n\n👉 Follow for daily Python quizzes!\n#python #softwaredeveloper #coding"
    },
    {
        "quiz_id": "tuple_single_element_comma",
        "title": "Python Trap: Single Element Tuple",
        "question": "What is the output of this code?",
        "file_tab": "tuples.py",
        "code": "x = (42)\ny = (42,)\nprint(type(x) == type(y))",
        "badge_text": "Spot the difference!",
        "options": [
            {"letter": "A", "text": "True"},
            {"letter": "B", "text": "False"},
            {"letter": "C", "text": "TypeError"},
            {"letter": "D", "text": "SyntaxError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- (42) without a comma is just an integer in parentheses (type int)",
            "- (42,) with a comma is a 1-element tuple (type tuple)",
            "- int == tuple is False!"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: The single-element tuple gotcha!\n\n```python\nx = (42)\ny = (42,)\nprint(type(x) == type(y))\n```\n\nTrue or False? 👇\nOption A: True\nOption B: False\nOption C: TypeError\nOption D: SyntaxError\n\n💡 Explanation: Parentheses alone do not create a tuple—the comma does! x is an int, while y is a tuple, making equality False!\n\n👉 Follow for daily Python tips!\n#python #coding #tech"
    },
    {
        "quiz_id": "list_extend_returns_none",
        "title": "Python Gotcha: list.extend() In-Place",
        "question": "What is the output of this code?",
        "file_tab": "extend.py",
        "code": "lst = [1, 2]\nprint(lst.extend([3, 4]))",
        "badge_text": "In-place mutations!",
        "options": [
            {"letter": "A", "text": "[1, 2, 3, 4]"},
            {"letter": "B", "text": "None"},
            {"letter": "C", "text": "4"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- list.extend() mutates the list in-place",
            "- It returns None, NOT the mutated list!",
            "- Printing lst.extend(...) therefore prints None"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: list.extend() return value!\n\n```python\nlst = [1, 2]\nprint(lst.extend([3, 4]))\n```\n\nDrop your guess! 👇\nOption A: [1, 2, 3, 4]\nOption B: None\nOption C: 4\nOption D: TypeError\n\n💡 Explanation: Like .sort() and .append(), .extend() modifies the list in place and returns None by design in Python!\n\n👉 Follow for daily programming challenges!\n#python #coding #developer"
    },
    {
        "quiz_id": "walrus_operator_expression",
        "title": "Python Quiz: Walrus Operator Assignment",
        "question": "What is the output of this code?",
        "file_tab": "walrus.py",
        "code": "print((x := 5) * 2, x)",
        "badge_text": "Python 3.8+ Feature!",
        "options": [
            {"letter": "A", "text": "10 5"},
            {"letter": "B", "text": "10 10"},
            {"letter": "C", "text": "SyntaxError"},
            {"letter": "D", "text": "NameError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- The walrus operator ':=' assigns 5 to x and returns 5",
            "- (x := 5) * 2 evaluates to 10",
            "- x retains the value 5, resulting in: 10 5"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Walrus Operator! What does this output?\n\n```python\nprint((x := 5) * 2, x)\n```\n\nComment below! 👇\nOption A: 10 5\nOption B: 10 10\nOption C: SyntaxError\nOption D: NameError\n\n💡 Explanation: The walrus operator := assigns and returns the value in an expression!\n\n#python #coding #programming #developer"
    },
    {
        "quiz_id": "dict_union_precedence",
        "title": "Python Trap: Dict Union Key Precedence",
        "question": "What is the output of this code?",
        "file_tab": "dict_merge.py",
        "code": "d1 = {'a': 1, 'b': 2}\nd2 = {'b': 99, 'c': 3}\nprint((d1 | d2)['b'])",
        "badge_text": "Dict Merge!",
        "options": [
            {"letter": "A", "text": "2"},
            {"letter": "B", "text": "99"},
            {"letter": "C", "text": "None"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- The dict union operator '|' (Python 3.9+) merges dicts",
            "- Right-hand operand takes precedence on duplicate keys: 'b' becomes 99"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Dict Union operator precedence!\n\n```python\nd1 = {'a': 1, 'b': 2}\nd2 = {'b': 99, 'c': 3}\nprint((d1 | d2)['b'])\n```\n\nCan you get this right? 👇\nOption A: 2\nOption B: 99\nOption C: None\nOption D: TypeError\n\n💡 Explanation: In dict union (d1 | d2), values from the right operand override the left!\n\n#python #coding #pythonquiz"
    },
    {
        "quiz_id": "isinstance_bool_int_check",
        "title": "Python Trap: isinstance(True, int)",
        "question": "What is the output of this code?",
        "file_tab": "types.py",
        "code": "print(isinstance(True, int), isinstance(False, int))",
        "badge_text": "Bool Inheritance!",
        "options": [
            {"letter": "A", "text": "True True"},
            {"letter": "B", "text": "False False"},
            {"letter": "C", "text": "True False"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- In Python, bool is a direct subclass of int!",
            "- True is an instance of int, and False is an instance of int"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: Is bool an instance of int?\n\n```python\nprint(isinstance(True, int), isinstance(False, int))\n```\n\nDrop your guess! 👇\nOption A: True True\nOption B: False False\nOption C: True False\nOption D: TypeError\n\n💡 Explanation: In Python, bool inherits from int, so isinstance(True, int) is True!\n\n#python #programming #pythonquiz"
    },
    {
        "quiz_id": "round_bankers_rounding",
        "title": "Python Quiz: Banker's Rounding Trap",
        "question": "What is the output of this code?",
        "file_tab": "rounding.py",
        "code": "print(round(2.5), round(3.5))",
        "badge_text": "Round to even!",
        "options": [
            {"letter": "A", "text": "3 4"},
            {"letter": "B", "text": "2 4"},
            {"letter": "C", "text": "2 3"},
            {"letter": "D", "text": "3 3"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- Python uses round-half-to-even (Banker's rounding)",
            "- 2.5 rounds to nearest even integer: 2",
            "- 3.5 rounds to nearest even integer: 4"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Banker's Rounding!\n\n```python\nprint(round(2.5), round(3.5))\n```\n\nComment before the reveal! 👇\nOption A: 3 4\nOption B: 2 4\nOption C: 2 3\nOption D: 3 3\n\n💡 Explanation: Python's round() uses round-to-nearest-even to eliminate statistical bias!\n\n#python #coding #math #developer"
    },
    {
        "quiz_id": "string_strip_characters_set",
        "title": "Python Gotcha: str.strip() Characters",
        "question": "What is the output of this code?",
        "file_tab": "strip.py",
        "code": "s = 'banana'\nprint(s.strip('ba'))",
        "badge_text": "Strip vs Replace!",
        "options": [
            {"letter": "A", "text": "'nana'"},
            {"letter": "B", "text": "'nan'"},
            {"letter": "C", "text": "''"},
            {"letter": "D", "text": "'banana'"}
        ],
        "correct_idx": 1,
        "explanation_lines": [
            "- str.strip('ba') strips ANY character in the set {'b', 'a'} from both ends",
            "- Leading 'ba' stripped, trailing 'a' stripped, leaving 'nan'"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: How does str.strip() actually work?\n\n```python\ns = 'banana'\nprint(s.strip('ba'))\n```\n\nWhat is printed? 👇\nOption A: 'nana'\nOption B: 'nan'\nOption C: ''\nOption D: 'banana'\n\n💡 Explanation: strip() strips any character in the argument string, not the exact substring prefix!\n\n#python #developer #coding"
    },
    {
        "quiz_id": "list_reverse_slice_indices",
        "title": "Python Quiz: Reverse Slicing Bounds",
        "question": "What is the output of this code?",
        "file_tab": "slicing_bounds.py",
        "code": "lst = [10, 20, 30, 40, 50]\nprint(lst[3:1:-1])",
        "badge_text": "Slicing Trap!",
        "options": [
            {"letter": "A", "text": "[40, 30]"},
            {"letter": "B", "text": "[40, 30, 20]"},
            {"letter": "C", "text": "[30, 20]"},
            {"letter": "D", "text": "[]"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- Index 3 is 40; slice stops BEFORE index 1 (which is 20)",
            "- Step is -1, so it takes index 3 and index 2: [40, 30]"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Reverse slicing indices!\n\n```python\nlst = [10, 20, 30, 40, 50]\nprint(lst[3:1:-1])\n```\n\nCan you solve this? 👇\nOption A: [40, 30]\nOption B: [40, 30, 20]\nOption C: [30, 20]\nOption D: []\n\n💡 Explanation: Slices stop strictly BEFORE the stop index (index 1 is 20, so only indices 3 and 2 are included)!\n\n#python #coding #quiz"
    },
    {
        "quiz_id": "set_discard_nonexistent",
        "title": "Python Gotcha: set.discard() vs set.remove()",
        "question": "What is the output of this code?",
        "file_tab": "sets.py",
        "code": "s = {1, 2}\ns.discard(99)\nprint(len(s))",
        "badge_text": "Set Methods!",
        "options": [
            {"letter": "A", "text": "2"},
            {"letter": "B", "text": "KeyError"},
            {"letter": "C", "text": "1"},
            {"letter": "D", "text": "None"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- s.remove(x) raises KeyError if element is absent",
            "- s.discard(x) silently does nothing if element is absent!",
            "- len(s) remains 2"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: discard() vs remove()!\n\n```python\ns = {1, 2}\ns.discard(99)\nprint(len(s))\n```\n\nGuess the output! 👇\nOption A: 2\nOption B: KeyError\nOption C: 1\nOption D: None\n\n💡 Explanation: set.discard() never raises an error for missing elements, unlike set.remove()!\n\n#python #softwareengineer #coding"
    },
    {
        "quiz_id": "unpacking_starred_middle",
        "title": "Python Quiz: Starred Unpacking Rest",
        "question": "What is the output of this code?",
        "file_tab": "unpack.py",
        "code": "a, *b, c = [1, 2, 3, 4, 5]\nprint(b)",
        "badge_text": "Extended Unpacking!",
        "options": [
            {"letter": "A", "text": "[2, 3, 4]"},
            {"letter": "B", "text": "(2, 3, 4)"},
            {"letter": "C", "text": "[1, 2, 3, 4]"},
            {"letter": "D", "text": "SyntaxError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- 'a' captures first element (1), 'c' captures last element (5)",
            "- '*b' captures all intermediate elements as a list: [2, 3, 4]"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Extended unpacking with *!\n\n```python\na, *b, c = [1, 2, 3, 4, 5]\nprint(b)\n```\n\nComment below! 👇\nOption A: [2, 3, 4]\nOption B: (2, 3, 4)\nOption C: [1, 2, 3, 4]\nOption D: SyntaxError\n\n💡 Explanation: Starred expressions capture remaining elements as a list!\n\n#python #programming #code"
    },
    {
        "quiz_id": "dict_keys_intersection_operator",
        "title": "Python Trap: Dict Keys Set Intersection",
        "question": "What is the output of this code?",
        "file_tab": "keys_view.py",
        "code": "d1 = {'x': 1, 'y': 2}\nd2 = {'y': 3, 'z': 4}\nprint(list(d1.keys() & d2.keys()))",
        "badge_text": "Dict Views!",
        "options": [
            {"letter": "A", "text": "['y']"},
            {"letter": "B", "text": "TypeError"},
            {"letter": "C", "text": "['x', 'y', 'z']"},
            {"letter": "D", "text": "[]"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- dict.keys() returns a set-like dictionary view",
            "- Bitwise '&' computes the set intersection of keys: {'y'}"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Dict keys set intersection!\n\n```python\nd1 = {'x': 1, 'y': 2}\nd2 = {'y': 3, 'z': 4}\nprint(list(d1.keys() & d2.keys()))\n```\n\nWhat is the output? 👇\nOption A: ['y']\nOption B: TypeError\nOption C: ['x', 'y', 'z']\nOption D: []\n\n💡 Explanation: Dictionary keys views support set operations like & (intersection) directly!\n\n#python #coding #tech"
    },
    {
        "quiz_id": "closure_nonlocal_mutation",
        "title": "Python Gotcha: nonlocal Scope Mutation",
        "question": "What is the output of this code?",
        "file_tab": "scope.py",
        "code": "def outer():\n    x = 10\n    def inner():\n        nonlocal x\n        x += 5\n    inner()\n    return x\n\nprint(outer())",
        "badge_text": "Scope Trap!",
        "options": [
            {"letter": "A", "text": "15"},
            {"letter": "B", "text": "10"},
            {"letter": "C", "text": "UnboundLocalError"},
            {"letter": "D", "text": "None"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- 'nonlocal' causes identifiers to refer to previously bound variables in the nearest enclosing scope",
            "- inner() modifies outer's x directly: 10 + 5 = 15"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: nonlocal keyword in closures!\n\n```python\ndef outer():\n    x = 10\n    def inner():\n        nonlocal x\n        x += 5\n    inner()\n    return x\n\nprint(outer())\n```\n\nDrop your guess! 👇\nOption A: 15\nOption B: 10\nOption C: UnboundLocalError\nOption D: None\n\n💡 Explanation: nonlocal binds to the outer enclosing scope variable!\n\n#python #developer #coding"
    },
    {
        "quiz_id": "class_variable_instance_shadow",
        "title": "Python Gotcha: Class vs Instance Attribute",
        "question": "What is the output of this code?",
        "file_tab": "oop.py",
        "code": "class Box:\n    val = 1\n\nb1 = Box()\nb1.val = 2\nprint(Box.val, b1.val)",
        "badge_text": "OOP Shadowing!",
        "options": [
            {"letter": "A", "text": "1 2"},
            {"letter": "B", "text": "2 2"},
            {"letter": "C", "text": "1 1"},
            {"letter": "D", "text": "AttributeError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- b1.val = 2 creates an INSTANCE attribute that shadows the class attribute",
            "- Box.val remains untouched at 1!"
        ],
        "narration": "",
        "caption": "🔥 Python Gotcha: Class variable shadowing!\n\n```python\nclass Box:\n    val = 1\n\nb1 = Box()\nb1.val = 2\nprint(Box.val, b1.val)\n```\n\nWhat is the output? 👇\nOption A: 1 2\nOption B: 2 2\nOption C: 1 1\nOption D: AttributeError\n\n💡 Explanation: Assigning to an instance attribute shadows the class attribute on that instance only!\n\n#python #coding #programming"
    },
    {
        "quiz_id": "enumerate_start_offset_index",
        "title": "Python Quiz: enumerate() Start Parameter",
        "question": "What is the output of this code?",
        "file_tab": "enum_test.py",
        "code": "items = ['cat', 'dog']\nprint(list(enumerate(items, start=1))[0])",
        "badge_text": "Builtin Functions!",
        "options": [
            {"letter": "A", "text": "(1, 'cat')"},
            {"letter": "B", "text": "(0, 'cat')"},
            {"letter": "C", "text": "('cat', 1)"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- enumerate(..., start=1) starts counting from index 1",
            "- The first tuple is (1, 'cat')"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: enumerate start index!\n\n```python\nitems = ['cat', 'dog']\nprint(list(enumerate(items, start=1))[0])\n```\n\nComment your answer! 👇\nOption A: (1, 'cat')\nOption B: (0, 'cat')\nOption C: ('cat', 1)\nOption D: TypeError\n\n#python #coding #developer"
    },
    {
        "quiz_id": "bool_arithmetic_addition",
        "title": "Python Trap: Boolean Math Addition",
        "question": "What is the output of this code?",
        "file_tab": "bool_math.py",
        "code": "print(True + True + False + True)",
        "badge_text": "Booleans in Math!",
        "options": [
            {"letter": "A", "text": "3"},
            {"letter": "B", "text": "True"},
            {"letter": "C", "text": "TypeError"},
            {"letter": "D", "text": "'TrueTrueFalseTrue'"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- In arithmetic expressions, True coerces to integer 1, and False coerces to 0",
            "- 1 + 1 + 0 + 1 = 3"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: What is True + True + False + True?\n\n```python\nprint(True + True + False + True)\n```\n\nDrop your guess! 👇\nOption A: 3\nOption B: True\nOption C: TypeError\nOption D: 'TrueTrueFalseTrue'\n\n💡 Explanation: True is 1 and False is 0 in numerical arithmetic!\n\n#python #programming #pythonquiz"
    },
    {
        "quiz_id": "set_symmetric_difference_xor",
        "title": "Python Quiz: Set Symmetric Difference",
        "question": "What is the output of this code?",
        "file_tab": "symm.py",
        "code": "s1 = {1, 2, 3}\ns2 = {2, 3, 4}\nprint(sorted(list(s1 ^ s2)))",
        "badge_text": "Set Operators!",
        "options": [
            {"letter": "A", "text": "[1, 4]"},
            {"letter": "B", "text": "[2, 3]"},
            {"letter": "C", "text": "[1, 2, 3, 4]"},
            {"letter": "D", "text": "[]"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- The '^' operator returns the symmetric difference (elements in either set, but not both)",
            "- 2 and 3 are in both, leaving 1 and 4 -> [1, 4]"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Set Symmetric Difference!\n\n```python\ns1 = {1, 2, 3}\ns2 = {2, 3, 4}\nprint(sorted(list(s1 ^ s2)))\n```\n\nWhat is the output? 👇\nOption A: [1, 4]\nOption B: [2, 3]\nOption C: [1, 2, 3, 4]\nOption D: []\n\n#python #softwareengineer #coding"
    },
    {
        "quiz_id": "dict_setdefault_existing_key",
        "title": "Python Trap: dict.setdefault() Existing Key",
        "question": "What is the output of this code?",
        "file_tab": "setdefault.py",
        "code": "d = {'count': 10}\nres = d.setdefault('count', 99)\nprint(res, d['count'])",
        "badge_text": "Dictionary Gotcha!",
        "options": [
            {"letter": "A", "text": "10 10"},
            {"letter": "B", "text": "99 99"},
            {"letter": "C", "text": "10 99"},
            {"letter": "D", "text": "None 10"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- If key exists, setdefault() returns existing value and does NOT modify the dict!",
            "- 'count' is already 10, so it returns 10 and stays 10"
        ],
        "narration": "",
        "caption": "🔥 Python Trap: dict.setdefault() with existing key!\n\n```python\nd = {'count': 10}\nres = d.setdefault('count', 99)\nprint(res, d['count'])\n```\n\nCan you solve this? 👇\nOption A: 10 10\nOption B: 99 99\nOption C: 10 99\nOption D: None 10\n\n#python #coding #tech"
    },
    {
        "quiz_id": "string_find_missing_return",
        "title": "Python Quiz: str.find() Missing Substring",
        "question": "What is the output of this code?",
        "file_tab": "find.py",
        "code": "s = 'python'\nprint(s.find('z'))",
        "badge_text": "Strings Trap!",
        "options": [
            {"letter": "A", "text": "-1"},
            {"letter": "B", "text": "ValueError"},
            {"letter": "C", "text": "False"},
            {"letter": "D", "text": "None"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- str.find() returns -1 when the substring is not found",
            "- (Unlike str.index() which raises ValueError)"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: find() vs index()!\n\n```python\ns = 'python'\nprint(s.find('z'))\n```\n\nDrop your guess! 👇\nOption A: -1\nOption B: ValueError\nOption C: False\nOption D: None\n\n💡 Explanation: str.find() returns -1 for missing items, while str.index() raises ValueError!\n\n#python #programming #code"
    },
    {
        "quiz_id": "lambda_default_arg_late_binding_fix",
        "title": "Python Quiz: Fixing Late Binding in Lambdas",
        "question": "What is the output of this code?",
        "file_tab": "fixed_lambda.py",
        "code": "funcs = [lambda x=i: x for i in range(3)]\nprint([f() for f in funcs])",
        "badge_text": "Lambda Fix!",
        "options": [
            {"letter": "A", "text": "[0, 1, 2]"},
            {"letter": "B", "text": "[2, 2, 2]"},
            {"letter": "C", "text": "[3, 3, 3]"},
            {"letter": "D", "text": "TypeError"}
        ],
        "correct_idx": 0,
        "explanation_lines": [
            "- Using default parameter 'x=i' evaluates 'i' at function definition time!",
            "- This fixes late binding and captures each loop value: [0, 1, 2]"
        ],
        "narration": "",
        "caption": "🔥 Python Quiz: Fixing closure late binding with default arguments!\n\n```python\nfuncs = [lambda x=i: x for i in range(3)]\nprint([f() for f in funcs])\n```\n\nWhat is the output? 👇\nOption A: [0, 1, 2]\nOption B: [2, 2, 2]\nOption C: [3, 3, 3]\nOption D: TypeError\n\n#python #softwareengineer #coding"
    }
]


class QuizManager:
    """Manages deduplication and provides never-before-posted quizzes with AI generation and LRU fallback."""

    def __init__(self):
        POSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.posted_file = POSTED_FILE

    def get_posted_quiz_records(self) -> List[Dict[str, Any]]:
        """Return list of all posted quiz record metadata from local cache and MongoDB Atlas."""
        records = []
        seen_keys = set()

        # 1. Local JSON file
        if self.posted_file.exists():
            try:
                with open(self.posted_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        qid = item.get("quiz_id") or ""
                        title = (item.get("title") or "").strip().lower()
                        key = f"{qid}::{title}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            records.append(item)
            except Exception as e:
                logger.warning(f"[QuizManager] Local read error: {e}")

        # 2. MongoDB Atlas Cloud database
        try:
            from pymongo import MongoClient
            from backend.app.config import settings
            if settings.mongodb_uri and not settings.mongodb_uri.startswith("mock"):
                client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
                db = client[settings.mongodb_db_name]

                for doc in db.posted_quizzes.find():
                    qid = doc.get("quiz_id") or ""
                    title = (doc.get("title") or "").strip().lower()
                    key = f"{qid}::{title}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        records.append({
                            "quiz_id": qid,
                            "title": doc.get("title"),
                            "code_hash": doc.get("code_hash"),
                            "posted_at": doc.get("posted_at") or doc.get("created_at"),
                            "instagram_url": doc.get("instagram_url")
                        })
        except Exception as e:
            logger.warning(f"[QuizManager] MongoDB sync note: {e}")

        return records

    def get_posted_quiz_ids(self) -> List[str]:
        """Return list of all exact quiz_ids that have already been posted."""
        records = self.get_posted_quiz_records()
        return [r["quiz_id"] for r in records if r.get("quiz_id")]

    def is_duplicate_or_posted(self, quiz: Dict[str, Any]) -> bool:
        """Strict check whether a quiz has already been published to Instagram."""
        records = self.get_posted_quiz_records()
        quiz_id = quiz.get("quiz_id")
        title_norm = (quiz.get("title") or "").strip().lower()

        code_str = quiz.get("code") or ""
        code_hash = hashlib.sha256(code_str.strip().encode()).hexdigest() if code_str else None

        for r in records:
            # Match exact quiz_id
            if quiz_id and r.get("quiz_id") == quiz_id:
                return True
            # Match exact normalized title
            if title_norm and (r.get("title") or "").strip().lower() == title_norm:
                return True
            # Match exact code hash
            if code_hash and r.get("code_hash") == code_hash:
                return True

        return False

    def is_posted(self, quiz_id: str) -> bool:
        """Check if a quiz_id has already been posted to Instagram."""
        return quiz_id in self.get_posted_quiz_ids()

    def record_posted_quiz(
        self,
        quiz_id: str,
        title: str,
        media_id: str,
        instagram_url: str,
        file_path: Optional[str] = None,
        code: Optional[str] = None
    ) -> None:
        """Record a posted quiz in both local cache and MongoDB Atlas to prevent duplicates."""
        posted_data = []
        if self.posted_file.exists():
            try:
                with open(self.posted_file, "r", encoding="utf-8") as f:
                    posted_data = json.load(f)
            except Exception:
                posted_data = []

        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(settings.timezone)
            now_local = datetime.now(tz)
        except Exception:
            now_local = datetime.now()

        now_local_iso = now_local.isoformat()
        now_utc_iso = datetime.now(timezone.utc).isoformat()
        local_time_display = now_local.strftime("%I:%M %p %Z")
        code_hash = hashlib.sha256(code.strip().encode()).hexdigest() if code else None

        title_norm = title.strip().lower()
        if not any((item.get("quiz_id") == quiz_id or (item.get("title") or "").strip().lower() == title_norm) for item in posted_data):
            record = {
                "quiz_id": quiz_id,
                "title": title,
                "media_id": media_id,
                "instagram_url": instagram_url,
                "file_path": file_path,
                "code_hash": code_hash,
                "posted_at": now_local_iso,
                "posted_at_utc": now_utc_iso,
                "local_time_display": local_time_display
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
                        "code_hash": code_hash,
                        "posted_at": now_local_iso,
                        "posted_at_utc": now_utc_iso,
                        "local_time_display": local_time_display
                    }},
                    upsert=True
                )
        except Exception as e:
            logger.warning(f"[QuizManager] MongoDB write note: {e}")

        logger.info(f"[QuizManager] Registered posted quiz '{quiz_id}' to prevent duplicates.")

    async def get_next_unposted_quiz_async(self) -> Dict[str, Any]:
        """Find the next fresh, never-posted quiz.
        Order of priority:
        1. AI Dynamic Generation (OpenRouter).
        2. Next unposted curated quiz from expanded bank.
        3. True LRU (Least Recently Used) rotation across all 50+ curated quizzes.
        """
        records = self.get_posted_quiz_records()
        posted_ids = {r.get("quiz_id") for r in records if r.get("quiz_id")}
        posted_titles = {(r.get("title") or "").strip().lower() for r in records if r.get("title")}
        posted_hashes = {r.get("code_hash") for r in records if r.get("code_hash")}

        # 1. AI Dynamic Generation first
        try:
            from backend.app.pipeline.ai_quiz_generator import AIQuizGenerator
            ai_gen = AIQuizGenerator()
            ai_quiz = await ai_gen.generate_quiz(
                exclude_titles=list(posted_titles),
                exclude_hashes=list(posted_hashes)
            )
            if ai_quiz and not self.is_duplicate_or_posted(ai_quiz):
                logger.info(f"[QuizManager] AI dynamically generated a novel unique quiz: '{ai_quiz['title']}'")
                return ai_quiz
        except Exception as e:
            logger.warning(f"[QuizManager] AI dynamic generator note: {e}")

        # 2. Curated pool: find first truly unposted quiz
        for quiz in CURATED_QUIZZES:
            q_id = quiz["quiz_id"]
            q_title = quiz["title"].strip().lower()
            code_hash = hashlib.sha256(quiz["code"].strip().encode()).hexdigest()

            if q_id not in posted_ids and q_title not in posted_titles and code_hash not in posted_hashes:
                logger.info(f"[QuizManager] Selected fresh unposted curated quiz: '{q_id}' - {quiz['title']}")
                return dict(quiz)

        # 3. If all curated quizzes have been posted, select the Least-Recently-Used (LRU) quiz
        logger.warning("[QuizManager] All curated quizzes have been posted once! Selecting the oldest published quiz (LRU rotation)...")
        quiz_last_posted = {}
        for r in records:
            qid = r.get("quiz_id", "")
            title = (r.get("title") or "").strip().lower()
            ts = str(r.get("posted_at") or r.get("created_at") or "1970-01-01")

            for q in CURATED_QUIZZES:
                if q["quiz_id"] == qid or q["title"].strip().lower() == title:
                    quiz_last_posted[q["quiz_id"]] = max(quiz_last_posted.get(q["quiz_id"], "1970-01-01"), ts)

        sorted_curated = sorted(CURATED_QUIZZES, key=lambda q: quiz_last_posted.get(q["quiz_id"], "1970-01-01"))
        chosen = dict(sorted_curated[0])
        logger.info(f"[QuizManager] LRU Selected: '{chosen['quiz_id']}' (last posted on: {quiz_last_posted.get(chosen['quiz_id'])})")
        return chosen

    def get_next_unposted_quiz(self) -> Dict[str, Any]:
        """Synchronous wrapper for get_next_unposted_quiz_async."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If running inside active loop, iterate curated pool directly
                records = self.get_posted_quiz_records()
                posted_ids = {r.get("quiz_id") for r in records if r.get("quiz_id")}
                posted_titles = {(r.get("title") or "").strip().lower() for r in records if r.get("title")}

                for quiz in CURATED_QUIZZES:
                    if quiz["quiz_id"] not in posted_ids and quiz["title"].strip().lower() not in posted_titles:
                        return dict(quiz)

                return dict(CURATED_QUIZZES[0])
            else:
                return loop.run_until_complete(self.get_next_unposted_quiz_async())
        except Exception:
            return asyncio.run(self.get_next_unposted_quiz_async())

