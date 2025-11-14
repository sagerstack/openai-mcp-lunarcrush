"""Module entry point for hello_world package."""

from hello_world.main import main


def main_entry() -> int:
    """Entry point for Poetry script."""
    return main()


if __name__ == "__main__":
    import sys

    sys.exit(main())
