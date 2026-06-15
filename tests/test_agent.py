"""Tests for the command-line agent."""

from __future__ import annotations

from internal_acronym_explainer import agent


def test_get_prompt_uses_first_passed_argument() -> None:
    """Verify only the first argument after the module name becomes the prompt."""
    prompt = agent._get_prompt(["What is CSS?", "extra"])

    assert prompt == "What is CSS?"


def test_get_prompt_returns_empty_string_without_arguments() -> None:
    """Verify missing arguments are treated as an empty prompt."""
    prompt = agent._get_prompt([])

    assert prompt == ""
