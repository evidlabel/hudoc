from unittest.mock import patch
import pytest
from hudoc.cli import download_callback, list_callback, latest_callback


def test_download_callback_file_not_exist():
    """Test download_callback when RSS file does not exist."""
    with (
        patch("sys.exit") as mock_exit,
        patch("hudoc.cli.logging") as mock_logging,
        patch("hudoc.cli.Path.is_file", return_value=False),
    ):
        download_callback("nonexistent.xml")
        mock_logging.error.assert_called_with(
            "RSS file 'nonexistent.xml' does not exist or is not a file."
        )
        mock_exit.assert_called_with(1)


def test_download_callback_exception():
    """Test download_callback when an exception occurs in process_rss."""
    with (
        patch("hudoc.cli.Path.is_file", return_value=True),
        patch("hudoc.cli.process_rss", side_effect=Exception("Test error")),
        patch("sys.exit") as mock_exit,
        patch("hudoc.cli.logging") as mock_logging,
    ):
        download_callback("rss.xml")
        mock_logging.error.assert_called_with("An error occurred: Test error")
        mock_exit.assert_called_with(1)


@pytest.mark.skip(reason="Patch not working for isfile")
def test_list_callback_file_not_exist():
    """Test list_callback when RSS file does not exist."""
    with (
        patch("sys.exit") as mock_exit,
        patch("hudoc.cli.logging") as mock_logging,
        patch("hudoc.cli.isfile", side_effect=lambda path: False),
    ):
        list_callback("nonexistent.xml")
        mock_logging.error.assert_called_with(
            "RSS file 'nonexistent.xml' does not exist or is not a file."
        )
        mock_exit.assert_called_with(1)


def test_list_callback_no_subsite():
    """Test list_callback with no subsite."""
    with (
        patch("hudoc.cli.isfile", side_effect=lambda path: True),
        patch("hudoc.cli.parse_rss_file", return_value=(None, [])),
        patch("sys.exit") as mock_exit,
        patch("hudoc.cli.logging") as mock_logging,
    ):
        list_callback("rss.xml")
        mock_logging.error.assert_called_with("Failed to detect subsite or parse items")
        mock_exit.assert_called_with(1)


def test_list_callback_no_items(capsys):
    """Test list_callback with no items."""
    with (
        patch("hudoc.cli.isfile", side_effect=lambda path: True),
        patch("hudoc.cli.parse_rss_file", return_value=("echr", [])),
        patch("hudoc.cli.logging") as mock_logging,
    ):
        list_callback("rss.xml")
        mock_logging.info.assert_called_with("No items found in RSS file")


def test_list_callback_with_items(capsys):
    """Test list_callback with items."""
    items = [{"doc_id": "001-123456", "title": "Test Case"}]
    with (
        patch("hudoc.cli.isfile", side_effect=lambda path: True),
        patch("hudoc.cli.parse_rss_file", return_value=("echr", items)),
    ):
        list_callback("rss.xml")
        captured = capsys.readouterr()
        assert "Document IDs:" in captured.out
        assert "- 001-123456 (Title: Test Case)" in captured.out
        assert "Subsite: echr" in captured.out
        assert "Number of items: 1" in captured.out


def test_latest_callback():
    """Test latest_callback downloads from the correct subsite URL."""
    with patch("hudoc.cli.process_rss_url") as mock_process:
        latest_callback(
            subsite="echr",
            output_dir="data",
            limit=3,
            threads=10,
            plain=False,
        )
        mock_process.assert_called_once()
        call_kwargs = mock_process.call_args.kwargs
        assert "echr" in call_kwargs["url"]
        assert call_kwargs["output_dir"] == "data"
        assert call_kwargs["evid"] is True


def test_latest_callback_exception():
    """Test latest_callback exits on error."""
    with (
        patch("hudoc.cli.process_rss_url", side_effect=Exception("Network error")),
        patch("sys.exit") as mock_exit,
        patch("hudoc.cli.logging") as mock_logging,
    ):
        latest_callback(
            subsite="echr", output_dir="data", limit=3, threads=10, plain=False
        )
        mock_logging.error.assert_called_with("An error occurred: Network error")
        mock_exit.assert_called_with(1)


def test_main():
    """Test main function runs the CLI."""
    from treeparse import cli_runner
    from hudoc.cli import app

    runner = cli_runner(app)
    result = runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "hudoc" in result.output
