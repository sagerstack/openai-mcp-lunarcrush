"""Main entry point for the Hello World console application."""

import sys


def main() -> int:
    """
    Main entry point for the hello world application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Default behavior - display "Hello, World!"
    message = "Hello, World!"

    # If arguments are provided, use them as custom messages
    if len(sys.argv) > 1:
        messages = sys.argv[1:]
        message = " ".join(messages)

    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
