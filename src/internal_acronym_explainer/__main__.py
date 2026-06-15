"""Bootstrap the command-line application."""

import asyncio

from . import agent


def main() -> None:
    """Run the command-line application."""
    asyncio.run(agent.main())


if __name__ == "__main__":
    main()
