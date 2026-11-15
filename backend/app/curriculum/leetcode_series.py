"""LeetCode Visual Explainer Curriculum Series for Instagram Reels.

Pedagogy:
- Designed specifically for students & interview candidates.
- Zero confusing syntax errors: pure algorithmic intuition!
- Stickman stands beside the code window, points at each line.
- Text callout bubbles appear line-by-line explaining WHAT each line does and WHY.
- Closes with Emerald Green Accepted output, YAAAYYY celebration, and Complexity Takeaways.
"""

from typing import Dict, Any, List

LEETCODE_CURRICULUM: List[Dict[str, Any]] = [
    {
        "problem_id": 1,
        "title": "LeetCode #1: Two Sum",
        "difficulty": "Easy",
        "pattern": "Hash Map Complement Lookup",
        "time_complexity": "O(N) Linear Time",
        "space_complexity": "O(N) Hash Map",
        "filename": "two_sum.py",
        "prompt_lines": [
            "# Given nums = [2, 7, 11, 15], target = 9",
            "# Return indices of the two numbers that add up to target"
        ],
        "solution_steps": [
            ("seen = {}", "Create an empty Hash Map for O(1) instant lookups"),
            ("for i, num in enumerate(nums):", "Check every number along with its index"),
            ("    diff = target - num", "What partner number do we need to reach target?"),
            ("    if diff in seen:", "If partner is in map, we found the pair!"),
            ("        return [seen[diff], i]", "Return both indices! Done!"),
            ("    seen[num] = i", "Otherwise, store number and index for later")
        ],
        "terminal_output": "[Accepted] Runtime: 38ms (Beats 98.4%)",
        "takeaway_l1": "1. Use Hash Map {num: index} for O(N) lookup speed",
        "takeaway_l2": "2. Avoids slow O(N²) nested loops completely",
        "next_teaser": "LeetCode #9: Palindrome Number"
    },
    {
        "problem_id": 9,
        "title": "LeetCode #9: Palindrome Number",
        "difficulty": "Easy",
        "pattern": "String Slicing Reversal",
        "time_complexity": "O(N) Time",
        "space_complexity": "O(N) Space",
        "filename": "is_palindrome.py",
        "prompt_lines": [
            "# Given integer x = 121",
            "# Return True if x reads same backward and forward"
        ],
        "solution_steps": [
            ("if x < 0:", "Negative numbers can never be palindromes (-121 != 121-)"),
            ("    return False", "Instant early exit for negatives!"),
            ("s = str(x)", "Convert integer to text string"),
            ("return s == s[::-1]", "Check if original equals reversed string [::-1]!")
        ],
        "terminal_output": "[Accepted] Runtime: 45ms (Beats 99.1%)",
        "takeaway_l1": "1. Negative numbers can never be palindromes",
        "takeaway_l2": "2. s[::-1] reverses strings in 1 clean line of Python",
        "next_teaser": "LeetCode #20: Valid Parentheses"
    },
    {
        "problem_id": 20,
        "title": "LeetCode #20: Valid Parentheses",
        "difficulty": "Easy",
        "pattern": "LIFO Stack Matching",
        "time_complexity": "O(N) Time",
        "space_complexity": "O(N) Stack",
        "filename": "valid_parentheses.py",
        "prompt_lines": [
            "# Given string s = '()[]{}'",
            "# Return True if brackets close in correct order"
        ],
        "solution_steps": [
            ("stack = []", "Create a list as a Last-In First-Out (LIFO) Stack"),
            ("pairs = {')': '(', ']': '[', '}': '{'}", "Map closing brackets to their matching open partners"),
            ("for char in s:", "Scan each bracket in the string one-by-one"),
            ("    if char in pairs:", "If closing: must match top of stack!"),
            ("        if not stack or stack.pop() != pairs[char]:", "Mismatch or empty stack? Return False!"),
            ("            return False", "Invalid bracket sequence detected!"),
            ("    else: stack.append(char)", "If opening bracket: push onto stack!"),
            ("return len(stack) == 0", "Empty stack at end confirms all brackets closed!")
        ],
        "terminal_output": "[Accepted] Runtime: 32ms (Beats 97.8%)",
        "takeaway_l1": "1. Stacks are the #1 data structure for matching brackets",
        "takeaway_l2": "2. Empty stack at end guarantees valid closed syntax",
        "next_teaser": "LeetCode #217: Contains Duplicate"
    },
    {
        "problem_id": 217,
        "title": "LeetCode #217: Contains Duplicate",
        "difficulty": "Easy",
        "pattern": "Set Deduplication Lookup",
        "time_complexity": "O(N) Time",
        "space_complexity": "O(N) Set",
        "filename": "contains_duplicate.py",
        "prompt_lines": [
            "# Given array nums = [1, 2, 3, 1]",
            "# Return True if any value appears at least twice"
        ],
        "solution_steps": [
            ("seen = set()", "Create an empty Set for O(1) membership testing"),
            ("for n in nums:", "Loop through each number in the array"),
            ("    if n in seen:", "If already in our set, duplicate found!"),
            ("        return True", "Instant early return True!"),
            ("    seen.add(n)", "Otherwise, remember current number in set"),
            ("return False", "No duplicates found after checking all numbers")
        ],
        "terminal_output": "[Accepted] Runtime: 39ms (Beats 98.6%)",
        "takeaway_l1": "1. Sets provide O(1) instant duplicate checks",
        "takeaway_l2": "2. One-line alternative: return len(nums) != len(set(nums))",
        "next_teaser": "LeetCode #121: Best Time to Buy and Sell Stock"
    },
    {
        "problem_id": 121,
        "title": "LeetCode #121: Buy & Sell Stock",
        "difficulty": "Easy",
        "pattern": "Single-Pass Greedy Tracking",
        "time_complexity": "O(N) Time",
        "space_complexity": "O(1) Space",
        "filename": "max_profit.py",
        "prompt_lines": [
            "# Given prices = [7, 1, 5, 3, 6, 4]",
            "# Return maximum profit from 1 buy and 1 sell"
        ],
        "solution_steps": [
            ("min_price = float('inf')", "Track the cheapest buy price seen so far"),
            ("max_profit = 0", "Track the highest profit achieved so far"),
            ("for price in prices:", "Scan daily stock prices in order"),
            ("    min_price = min(min_price, price)", "Update cheapest day to buy"),
            ("    profit = price - min_price", "Calculate profit if sold today"),
            ("    max_profit = max(max_profit, profit)", "Update record maximum profit"),
            ("return max_profit", "Return the best profit found!")
        ],
        "terminal_output": "[Accepted] Runtime: 48ms (Beats 96.9%)",
        "takeaway_l1": "1. Track minimum price seen so far in single pass O(N)",
        "takeaway_l2": "2. Never buy after you sell (forward time flow)",
        "next_teaser": "LeetCode #125: Valid Palindrome"
    }
]
