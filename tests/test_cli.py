import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from hudoc.cli import main, download_callback, list_callback

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / ".." / "treeparse" / "src"))

from treeparse import cli as treeparse_cli


def test_download_callback_file_not_exist():
    """Test download_callback when RSS file does not exist."""
    with patch("sys.exit") as mock_exit, patch("hudoc.cli.logging") as mock_logging, \
         patch("hudoc.cli.Path.is_file", return_value=False):
        download_callback("nonexistent.xml")
        mock_logging.error.assert_called_with("RSS file 'nonexistent.xml' does not exist or is not a file.")
        mock_exit.assert_called_with(1)


def test_download_callback_exception():
    """Test download_callback when an exception occurs in process_rss."""
    with patch("hudoc.cli.Path.is_file", return_value=True), \
         patch("hudoc.cli.process_rss", side_effect=Exception("Test error")), \
         patch("sys.exit") as mock_exit, \
         patch("hudoc.cli.logging") as mock_logging:
        download_callback("rss.xml")
        mock_logging.error.assert_called_with("An error occurred: Test error")
        mock_exit.assert_called_with(1)


def test_list_callback_file_not_exist():
    """Test list_callback when RSS file does not exist."""
    with patch("sys.exit") as mock_exit, patch("hudoc.cli.logging") as mock_logging, \
         patch("hudoc.cli.Path.is_file", return_value=False):
        list_callback("nonexistent.xml")
        mock_logging.error.assert_called_with("RSS file 'nonexistent.xml' does not exist or is not a file.")
        mock_exit.assert_called_with(1)


def test_list_callback_no_subsite():
    """Test list_callback with no subsite."""
    with patch("hudoc.cli.Path.is_file", return_value=True), \
         patch("hudoc.cli.parse_rss_file", return_value=(None, [])), \
         patch("sys.exit") as mock_exit, \
         patch("hudoc.cli.logging") as mock_logging:
        list_callback("rss.xml")
        mock_logging.error.assert_called_with("Failed to detect subsite or parse items")
        mock_exit.assert_called_with(1)


def test_list_callback_no_items(capsys):
    """Test list_callback with no items."""
    with patch("hudoc.cli.Path.is_file", return_value=True), \
         patch("hudoc.cli.parse_rss_file", return_value=("echr", [])), \
         patch("hudoc.cli.logging") as mock_logging:
        list_callback("rss.xml")
        mock_logging.info.assert_called_with("No items found in RSS file")


def test_list_callback_with_items(capsys):
    """Test list_callback with items."""
    items = [{"doc_id": "001-123456", "title": "Test Case"}]
    with patch("hudoc.cli.Path.is_file", return_value=True), \
         patch("hudoc.cli.parse_rss_file", return_value=("echr", items)):
        list_callback("rss.xml")
        captured = capsys.readouterr()
        assert "Document IDs:" in captured.out
        assert "- 001-123456 (Title: Test Case)" in captured.out
        assert "Subsite: echr" in captured.out
        assert "Number of items: 1" in captured.out


def test_main(capsys):
    """Test main function runs the CLI."""
    with patch("sys.argv", ["hudoc", "--help"]), pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "hudoc" in captured.out
