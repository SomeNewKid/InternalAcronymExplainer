"""Tests for utility functions in the tools module."""

from __future__ import annotations

from internal_acronym_explainer.tools import get_words_from_prose


def test_get_words_from_prose_removes_basic_punctuation() -> None:
    prose = "Hello, world! This is a test."

    assert get_words_from_prose(prose) == ["Hello", "world", "This", "is", "a", "test"]


def test_get_words_from_prose_handles_apostrophes_and_hyphens() -> None:
    prose = "It's a high-quality write-up."

    assert get_words_from_prose(prose) == ["Its", "a", "high", "quality", "write", "up"]


def test_get_words_from_prose_returns_empty_for_no_words() -> None:
    assert get_words_from_prose("... ! ? ,") == []
