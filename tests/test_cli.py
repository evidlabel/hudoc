import sys
from pathlib import Path
from unittest.mock import patch

from hudoc.cli import main, download_callback

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent / ".." / "treeparse" / "src")
)



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


def test_main(capsys):
    """Test main function runs the CLI."""
    with patch("sys.argv", ["hudoc", "--help"]):
        main()
    captured = capsys.readouterr()
    assert "hudoc" in captured.out
