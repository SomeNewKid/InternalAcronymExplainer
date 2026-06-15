# Internal Acronym Explainer

Internal Acronym Explainer is a small Python command-line sample for exploring
guardrails in Google's Agent Development Kit. It accepts a question about an
acronym, asks a local tool for internal company meanings, and prints a short
answer that separates internal meanings from general meanings.

> [!WARNING]
> This is an experimental project and should not be considered production-ready.

The project was created to learn where ADK callback guardrails fit in an agent
workflow. The acronym domain is intentionally small so it is easy to see when a
guardrail runs and what it changes.

## What It Does

The CLI accepts a prompt such as:

```powershell
.\.venv\Scripts\python.exe -m internal_acronym_explainer "What does the acronym 'CSS' mean?"
```

The agent then:

- creates an in-memory ADK session
- sends the user's prompt to an ADK agent
- asks the `get_acronym_phrases` tool for internal acronym meanings
- applies guardrails before and after the agent run
- applies guardrails before and after LLM calls
- applies guardrails before and after tool calls
- prints the final response

The sample guardrails demonstrate how callbacks can block a run, replace a
response, rewrite a tool call, and filter sensitive tool results before they are
shown to the model.

## Guardrail Examples

The current guardrails are examples only:

- `before_agent_guardrail` blocks requests containing `XXX`.
- `after_agent_guardrail` replaces final output containing disallowed words.
- `before_model_guardtail` removes tool-result phrases containing `Directive`
  before the LLM sees them.
- `after_model_guardrail` rewrites a model-requested
  `get_acronym_phrases(acronym="LOG")` tool call to instead use the acronym `ETL`.
- `before_tool_guardrail` blocks `get_acronym_phrases` calls for `WTF`.
- `after_tool_guardrail` removes internal acronym phrases containing `Secret`.

These rules are deliberately artificial. They exist to make ADK callback timing
and data flow visible.

## Requirements

- Python 3.11.
- PowerShell on Windows.
- An `OPENAI_API_KEY` environment variable when `USE_REMOTE_OPENAI_MODEL` is
  enabled.
- A `GOOGLE_API_KEY` environment variable when using the default Gemini-backed
  ADK model.
- Ollama installed and running when `USE_LOCAL_GRANITE_MODEL` is enabled.

For the local Granite path, pull the model with:

```powershell
ollama pull granite3.3:8b
```

## Setup

Create the virtual environment and install the project with development
dependencies:

```powershell
.\scripts\setup-dev.ps1
```

The setup script expects Python 3.11 at the path configured in
`scripts\setup-dev.ps1`.

## Running

Run the agent from the repository root:

```powershell
.\.venv\Scripts\python.exe -m internal_acronym_explainer "What does the acronym 'CSS' mean?"
```

Example output includes a debug line from the local tool:

```text
Called get_acronym_phrases('CSS')
'CSS' has several meanings within the company...
```

The active model is controlled near the top of
`src/internal_acronym_explainer/agent.py`:

```python
USE_REMOTE_OPENAI_MODEL = True
USE_LOCAL_GRANITE_MODEL = False
REMOTE_OPENAI_MODEL = "gpt-4o"
LOCAL_GRANITE_MODEL = "ollama_chat/granite3.3:8b"
```

When both switches are false, the agent uses ADK's default Google model.

## Development Checks

Run formatting, linting, type checking, and tests:

```powershell
.\scripts\check.ps1
```

This runs:

- `ruff format .`
- `ruff check .`
- `pyright`
- `pytest`

## Project Structure

```text
src/internal_acronym_explainer/
  __main__.py    Package entry point for python -m internal_acronym_explainer
  agent.py       ADK agent setup, model selection, runner, and CLI entry point
  guardrails.py  Agent, model, and tool callback guardrails
  tools.py       Local acronym lookup tool and prose helpers

tests/
  test_agent.py
  test_guardrails.py
  test_smoke.py
  test_tools.py

scripts/
  setup-dev.ps1
  check.ps1
```

## Notes

This project is a guardrail learning exercise, not a real internal acronym
system. The acronym table is small, local, and intentionally contrived.

Different models may behave differently around tool use. In particular, hosted
and local models may not make the same tool-call decisions for unfamiliar
acronyms. That variability is useful for seeing which policies are deterministic
Python guardrails and which behaviors still depend on the model.

Hosted model calls may incur usage costs.

## Third-Party Notices

This project has a direct runtime dependency on the `google-adk` Python package,
including optional ADK extensions used for alternate model integrations. See the
package's PyPI license metadata for full license and notice terms.

## License

GNU General Public License v3.0. See the `LICENSE` file for details.
