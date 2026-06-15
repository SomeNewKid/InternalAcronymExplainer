"""Command-line interface for the application."""

from __future__ import annotations

import sys

from google.adk.agents import Agent
from google.adk.labs.openai import OpenAILlm
from google.adk.models import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.utils.content_utils import extract_text_from_content
from google.genai import types

from internal_acronym_explainer.guardrails import (
    after_agent_guardrail,
    after_model_guardrail,
    after_tool_guardrail,
    before_agent_guardrail,
    before_model_guardtail,
    before_tool_guardrail,
)
from internal_acronym_explainer.tools import get_acronym_phrases

USE_REMOTE_OPENAI_MODEL = True
USE_LOCAL_GRANITE_MODEL = False
REMOTE_OPENAI_MODEL = "gpt-4o"
LOCAL_GRANITE_MODEL = "ollama_chat/granite3.3:8b"


async def main(argv: list[str] | None = None) -> None:
    """Run the command-line interface."""
    prompt = _get_prompt(argv)
    if not prompt:
        example = "What does the acronym 'CSS' stand for?"
        raise SystemExit(f'Usage: python -m internal_acronym_explainer "{example}"')

    app_name = "internal_acronym_explainer"
    user_id = "cli_user"
    session_id = "cli_session"

    agent = Agent(
        name=app_name,
        description="Explains an acronym, both public and internal company acronyms.",
        instruction=(
            "You explain acronyms. "
            "For every user request, before answering, you must call the "
            "`get_acronym_phrases` tool with the acronym from the user's question. "
            "This is mandatory even if you believe the acronym is generic, unknown, "
            "made up, or has no internal meaning. "
            "Do not answer until the tool has been called. "
            "After using the tool, then use your own knowledge to identify "
            "further phrases associated with the acryonym. "
            "If the user provides the context in which the acronym was used, "
            "use this context to filter acronyms in your own knowedge, "
            "but do not use the context to filter company phrases "
            "returned by the tool. "
            "Reply to the user, with one paragraph explaining internal "
            "company uses of the acronym (if any), and a separate paragraph "
            "explaining more general uses of the acronym (those from your knowledge). "
        ),
        tools=[get_acronym_phrases],
        before_agent_callback=[before_agent_guardrail],
        after_agent_callback=[after_agent_guardrail],
        before_model_callback=[before_model_guardtail],
        after_model_callback=[after_model_guardrail],
        before_tool_callback=[before_tool_guardrail],
        after_tool_callback=[after_tool_guardrail],
    )
    if USE_REMOTE_OPENAI_MODEL:
        agent.model = OpenAILlm(model=REMOTE_OPENAI_MODEL)
    elif USE_LOCAL_GRANITE_MODEL:
        agent.model = LiteLlm(model=LOCAL_GRANITE_MODEL)

    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service,
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    final_text = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            final_text = extract_text_from_content(event.content)

    print(final_text)


def _get_prompt(argv: list[str] | None = None) -> str:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        return ""

    return args[0]
