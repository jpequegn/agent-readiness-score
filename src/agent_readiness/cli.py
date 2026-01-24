"""Command-line interface for agent-readiness-score."""

import sys


def main() -> None:
    """Main CLI entry point."""
    print("Agent Readiness Score v0.1.0")
    print("Core framework installed successfully!")
    print()
    print("Usage: agent-readiness <directory>")
    print()
    print("Note: Pillar implementations coming in future issues.")
    print("The core scanning framework is now ready for pillar development.")
    sys.exit(0)


if __name__ == "__main__":
    main()
