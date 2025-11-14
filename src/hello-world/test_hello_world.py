"""Test suite for hello-world package."""

import sys
from unittest.mock import patch
from hello_world.main import main
from hello_world.__main__ import main_entry
from hello_world import __version__


def test_version():
    """Test that version is correctly defined."""
    assert __version__ == "0.1.0"


def test_main_no_arguments(capsys):
    """Test main function with no arguments."""
    with patch.object(sys, 'argv', ['test']):
        result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert captured.out == "Hello, World!\n"


def test_main_with_arguments(capsys):
    """Test main function with custom arguments."""
    with patch.object(sys, 'argv', ['test', 'Custom', 'message', 'here']):
        result = main()
        captured = capsys.readouterr()
        assert result == 0
        assert captured.out == "Custom message here\n"


def test_main_entry_function(capsys):
    """Test main_entry function (Poetry script entry point)."""
    with patch.object(sys, 'argv', ['test', 'Hello', 'from', 'main_entry']):
        result = main_entry()
        captured = capsys.readouterr()
        assert result == 0
        assert captured.out == "Hello from main_entry\n"


def test_imports():
    """Test that all modules can be imported successfully."""
    # This test passes if no ImportError is raised
    import hello_world
    import hello_world.main
    import hello_world.__main__