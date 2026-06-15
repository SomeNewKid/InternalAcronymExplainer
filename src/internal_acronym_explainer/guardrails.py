from __future__ import annotations

import re
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.utils.content_utils import extract_text_from_content
from google.genai import types


def before_model_guardtail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """Remove tool-result phrases containing Directive before the LLM sees them."""
    for content in llm_request.contents:
        if not content.parts:
            continue

        for part in content.parts:
            if not part.function_response:
                continue

            function_response = part.function_response

            if function_response.name != "get_acronym_phrases":
                continue

            response = function_response.response

            if not isinstance(response, dict):
                continue

            result = response.get("result")

            if not isinstance(result, list):
                continue

            safe_result = []

            for phrase in result:
                if not isinstance(phrase, str):
                    safe_result.append(phrase)

                if "directive" in phrase.lower():
                    continue

                safe_result.append(phrase)

            response["result"] = safe_result

    return None


def after_model_guardrail(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """Rewrite get_acronym_phrases(acronym='LOG') tool calls to use ETL."""
    changed = False

    for function_call in llm_response.get_function_calls():
        if function_call.name != "get_acronym_phrases":
            continue

        if function_call.args is None:
            continue

        acronym = function_call.args.get("acronym")

        if not isinstance(acronym, str):
            continue

        if acronym.lower() != "log":
            continue

        function_call.args["acronym"] = "ETL"
        changed = True

    if changed:
        return llm_response

    return None


def before_tool_guardrail(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> dict[str, Any] | None:
    """Blocks get_acronym_phrases tool calls for the acronym WTF."""
    if tool.name != "get_acronym_phrases":
        return None

    acronym = args.get("acronym", "")

    if not isinstance(acronym, str):
        return None

    if acronym.lower() == "wtf":
        return {"result": ["The acronym WTF is blocked by the before-tool guardrail."]}

    return None


def after_tool_guardrail(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: Any,
) -> dict[str, Any] | None:
    """Blocks get_acronym_phrases tool calls returning secrets."""
    if tool.name != "get_acronym_phrases":
        return None

    if not isinstance(tool_response, list):
        return None

    safe_phrases = []
    omitted = 0

    for phrase in tool_response:
        if isinstance(phrase, str) and "secret" in phrase.lower():
            omitted += 1
            continue

        safe_phrases.append(phrase)

    if omitted == 0:
        return None

    return {"result": safe_phrases}


def before_agent_guardrail(callback_context: CallbackContext) -> types.Content | None:
    """Block the entire agent run if the user asks about XXX."""
    user_text = ""

    if callback_context.user_content:
        user_text = extract_text_from_content(callback_context.user_content)

    if "xxx" not in user_text.lower():
        return None

    return types.Content(
        role="model",
        parts=[
            types.Part(
                text=(
                    "I cannot process requests about the acronym XXX. "
                    "Please ask about a different acronym."
                )
            )
        ],
    )


def after_agent_guardrail(callback_context: CallbackContext) -> types.Content | None:
    """Replace the agent response if it contains disallowed words."""
    latest_agent_text = ""

    for event in reversed(callback_context.session.events):
        if event.author != callback_context.agent_name:
            continue

        if not event.content:
            continue

        latest_agent_text = extract_text_from_content(event.content)
        break

    normalized_text = latest_agent_text.lower()

    words = get_words_from_prose(normalized_text)

    for word in words:
        for disallowed in ("sex", "fuck"):
            if word.startswith(disallowed):
                return types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text=(
                                "I cannot provide the response "
                                "because it contains disallowed language. "
                                "Please try asking about a different acronym."
                            )
                        )
                    ],
                )

    return None


def get_words_from_prose(prose: str) -> list[str]:
    """Return words from English prose with punctuation removed."""
    if not prose:
        return []

    words: list[str] = []

    _WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

    for word in _WORD_PATTERN.findall(prose):
        words.append(word.replace("'", ""))

    return words
