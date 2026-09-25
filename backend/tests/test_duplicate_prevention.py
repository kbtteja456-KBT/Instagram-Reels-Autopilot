"""Tests for strict anti-duplicate detection and QuizManager guarantees."""

import pytest
from backend.app.pipeline.quiz_manager import QuizManager, CURATED_QUIZZES


def test_quiz_manager_anti_duplicate_check():
    qm = QuizManager()

    # Create dummy quiz record
    test_quiz = {
        "quiz_id": "test_unique_quiz_123",
        "title": "Python Quiz: Test Title Unique",
        "code": "print('hello_unique_world')",
        "question": "What is output?",
        "options": []
    }

    # Should not be duplicate initially
    assert qm.is_duplicate_or_posted(test_quiz) is False

    # Simulate recording it as posted
    qm.record_posted_quiz(
        quiz_id=test_quiz["quiz_id"],
        title=test_quiz["title"],
        media_id="mock_media_999",
        instagram_url="https://www.instagram.com/reel/mock123/",
        code=test_quiz["code"]
    )

    # Now it must be detected as duplicate by quiz_id
    assert qm.is_duplicate_or_posted(test_quiz) is True

    # Same title with different quiz_id must still be blocked as duplicate
    dup_title_quiz = dict(test_quiz)
    dup_title_quiz["quiz_id"] = "different_id_same_title"
    assert qm.is_duplicate_or_posted(dup_title_quiz) is True

    # Same code snippet with different title must still be blocked as duplicate
    dup_code_quiz = {
        "quiz_id": "brand_new_id",
        "title": "Brand New Title",
        "code": "print('hello_unique_world')"
    }
    assert qm.is_duplicate_or_posted(dup_code_quiz) is True


def test_next_unposted_quiz_never_returns_already_posted():
    qm = QuizManager()
    quiz = qm.get_next_unposted_quiz()
    assert quiz is not None
    assert "title" in quiz
    assert "code" in quiz
    assert "options" in quiz
