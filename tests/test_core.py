from pathlib import Path
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from hudoc.core.parser import parse_rss_file
from hudoc.core.processor import process_rss
from hudoc.core.downloader import download_document


def test_parse_rss_file_echr():
    """Test parsing an ECHR RSS file."""
    rss_file = Path("tests/data/echr_rss.xml")
    subsite, items = parse_rss_file(rss_file)
    assert subsite == "echr"
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-123456"
    assert items[0]["title"] == "CASE OF TEST v. TEST"
    assert items[0]["description"] == "12345/20 - Chamber Judgment"


def test_parse_rss_file_grevio():
    """Test parsing a GREVIO RSS file."""
    rss_file = Path("tests/data/grevio_rss.xml")
    subsite, items = parse_rss_file(rss_file)
    assert subsite == "grevio"
    assert len(items) == 1
    assert items[0]["doc_id"] == "TEST-2023-1"
    assert items[0]["title"] == "Test Report"
    assert items[0]["description"] == "Test Description"


def test_parse_rss_file_no_items():
    """Test parsing RSS with no items."""
    mock_root = MagicMock()
    mock_root.findall.return_value = []
    with (
        patch(
            "xml.etree.ElementTree.parse",
            return_value=MagicMock(getroot=lambda: mock_root),
        ),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("dummy.xml")
        assert subsite is None
        assert items == []
        mock_logging.warning.assert_called_with("No items found in RSS file")


def test_parse_rss_file_invalid_subsite():
    """Test parsing RSS with invalid subsite."""
    mock_item = MagicMock()
    mock_item.find.return_value.text = "https://hudoc.invalid.coe.int/eng#test"
    mock_root = MagicMock()
    mock_root.findall.return_value = [mock_item]
    with (
        patch(
            "xml.etree.ElementTree.parse",
            return_value=MagicMock(getroot=lambda: mock_root),
        ),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("dummy.xml")
        assert subsite is None
        assert items == []
        mock_logging.error.assert_called_with(
            "Error parsing RSS file: Invalid or unrecognized subsite in URL: https://hudoc.invalid.coe.int/eng#test"
        )


def test_parse_rss_file_no_link():
    """Test parsing RSS with no link in first item."""
    mock_item = MagicMock()
    mock_item.find.return_value = None
    mock_root = MagicMock()
    mock_root.findall.return_value = [mock_item]
    with (
        patch(
            "xml.etree.ElementTree.parse",
            return_value=MagicMock(getroot=lambda: mock_root),
        ),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("dummy.xml")
        assert subsite is None
        assert items == []
        mock_logging.error.assert_called_with(
            "Error parsing RSS file: First item has no link to detect subsite"
        )


def test_parse_rss_file_item_no_link():
    """Test parsing RSS item with no link."""
    mock_item = MagicMock()
    mock_item.find.side_effect = (
        lambda tag: None if tag == "link" else MagicMock(text="test")
    )
    mock_root = MagicMock()
    mock_root.findall.return_value = [
        MagicMock(
            find=lambda tag: MagicMock(text="https://hudoc.echr.coe.int/eng#test")
            if tag == "link"
            else None
        ),
        mock_item,
    ]
    with (
        patch(
            "xml.etree.ElementTree.parse",
            return_value=MagicMock(getroot=lambda: mock_root),
        ),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("dummy.xml")
        assert subsite == "echr"
        assert len(items) == 1
        mock_logging.warning.assert_called_with("Item has no link; skipping")


def test_parse_rss_file_invalid_pubdate():
    """Test parsing RSS with invalid pubDate."""

    def find_side_effect(tag):
        if tag == "link":
            elem = MagicMock()
            elem.text = 'https://hudoc.echr.coe.int/eng#{"itemid":"test"}'
            return elem
        if tag == "pubDate":
            elem = MagicMock()
            elem.text = "invalid date"
            return elem
        elem = MagicMock()
        elem.text = "test"
        return elem

    mock_item = MagicMock()
    mock_item.find.side_effect = find_side_effect
    mock_root = MagicMock()
    mock_root.findall.return_value = [mock_item]
    with (
        patch(
            "xml.etree.ElementTree.parse",
            return_value=MagicMock(getroot=lambda: mock_root),
        ),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("dummy.xml")
        assert subsite == "echr"
        assert len(items) == 1
        mock_logging.warning.assert_called_with(
            "Failed to parse pubDate: time data 'invalid date' does not match format '%a, %d %b %Y %H:%M:%S %z'"
        )


def test_parse_rss_file_invalid_fragment():
    """Test parsing RSS with invalid link fragment."""
    mock_item = MagicMock()
    mock_item.find.return_value.text = "https://hudoc.echr.coe.int/eng#invalid"
    mock_root = MagicMock()
    mock_root.findall.return_value = [mock_item]
    with (
        patch(
            "xml.etree.ElementTree.parse",
            return_value=MagicMock(getroot=lambda: mock_root),
        ),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("dummy.xml")
        assert subsite == "echr"
        assert items == []
        mock_logging.warning.assert_called_with(
            "Failed to parse item from link https://hudoc.echr.coe.int/eng#invalid: Expecting value: line 1 column 1 (char 0)"
        )


def test_parse_rss_file_parse_error():
    """Test parsing invalid RSS file."""
    with (
        patch("xml.etree.ElementTree.parse", side_effect=ET.ParseError("Parse error")),
        patch("hudoc.core.parser.logging") as mock_logging,
    ):
        subsite, items = parse_rss_file("invalid.xml")
        assert subsite is None
        assert items == []
        mock_logging.error.assert_called_with("Failed to parse RSS file: Parse error")


def test_parse_rss_file_file_not_found():
    """Test parsing non-existent RSS file."""
    with patch("hudoc.core.parser.logging") as mock_logging:
        subsite, items = parse_rss_file("nonexistent.xml")
        assert subsite is None
        assert items == []
        mock_logging.error.assert_called_with("RSS file not found: nonexistent.xml")


def test_process_rss_no_subsite():
    """Test process_rss with no subsite detected."""
    with (
        patch("hudoc.core.processor.parse_rss_file", return_value=(None, [])),
        patch("hudoc.core.processor.logging") as mock_logging,
    ):
        process_rss("rss.xml", "output")
        mock_logging.error.assert_called_with("Failed to detect subsite or parse items")


def test_process_rss_no_items():
    """Test process_rss with no items."""
    with (
        patch("hudoc.core.processor.parse_rss_file", return_value=("echr", [])),
        patch("hudoc.core.processor.logging") as mock_logging,
    ):
        process_rss("rss.xml", "output")
        mock_logging.error.assert_called_with("No items to process")


def test_process_rss_limit_zero():
    """Test process_rss with limit=0 (all items)."""
    items = [{"doc_id": "1"}, {"doc_id": "2"}]
    with (
        patch("hudoc.core.processor.parse_rss_file", return_value=("echr", items)),
        patch("hudoc.core.processor.ThreadPoolExecutor") as mock_executor,
    ):
        process_rss("rss.xml", "output", limit=0)
        assert mock_executor().__enter__().submit.call_count == 2


def test_process_rss_echr(tmp_path, requests_mock):
    """Test processing an ECHR RSS file with pre-downloaded content."""
    rss_file = Path("tests/data/echr_rss.xml")
    doc_id = "001-123456"
    output_dir = tmp_path / "output"

    with open("tests/data/echr_doc.html") as f:
        html_content = f.read()
    requests_mock.get(
        f"https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id={doc_id}",
        text=html_content,
    )

    process_rss(
        rss_file=rss_file,
        output_dir=output_dir,
        limit=3,
        threads=1,
        conversion_delay=2.0,
        evid=False,
    )
    output_file = output_dir / f"echr_doc_{doc_id}.txt"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Title: CASE OF TEST v. TEST" in content
    assert "ECHR Test Paragraph" in content


def test_download_document_no_text():
    """Test download_document when no text is retrieved."""
    item = {"doc_id": "test", "title": "Test", "description": "Test"}
    with (
        patch("hudoc.core.downloader.get_document_text", return_value=None),
        patch("hudoc.core.downloader.logging") as mock_logging,
    ):
        download_document(item, "echr", "output", 2.0, False)
        mock_logging.warning.assert_called_with("No content retrieved for test")
