from __future__ import annotations

import re

ACRONYM_PHRASES: list[tuple[str, str]] = [
    ("css", "Customer Survey Score"),
    ("css", "Computer Support Services"),
    ("api", "Annual Performance Index"),
    ("crm", "Client Readiness Matrix"),
    ("kpi", "Kitchen Pantry Inventory"),
    ("sla", "Staff Lunch Allocation"),
    ("roi", "Roster Overlap Indicator"),
    ("mvp", "Meeting Viability Protocol"),
    ("sso", "Secret Service Order"),
    ("sso", "Standard Stationery Order"),
    ("etl", "Escalation Triage Log"),
    ("ssd", "Special Service Directive"),
    ("ssd", "Seventy Seven Ducks"),
]

_WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def get_acronym_phrases(acronym: str) -> list[str]:
    """
    Returns a list of internal company phrases
    which are associated with the specified acronym.

    Args:
        acronym (str): the acronym for which to return associated phrases

    Returns:
        list[str]: the list of phrases associated with the acronym
    """
    print(f"Called get_acronym_phrases('{acronym}')")
    phrases: list[str] = []
    if not acronym:
        return phrases
    acronym = acronym.lower()

    for key, phrase in ACRONYM_PHRASES:
        if key == acronym:
            phrases.append(phrase)

    return phrases


def get_words_from_prose(prose: str) -> list[str]:
    """Return words from English prose with punctuation removed."""
    if not prose:
        return []

    words: list[str] = []
    for word in _WORD_PATTERN.findall(prose):
        words.append(word.replace("'", ""))

    return words
