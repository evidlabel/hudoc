from pathlib import Path
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from hudoc.core.parser import parse_rss_file, parse_rss_url
from hudoc.core.processor import download_document, process_rss, process_rss_url


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


def test_parse_rss_file_query_param_id(tmp_path):
    """Live HUDOC RSS uses ?i=<doc_id> instead of a JSON fragment."""
    rss_file = tmp_path / "echr_query.xml"
    rss_file.write_text(
        """<rss version="2.0">
    <channel>
        <item>
            <title>AFFAIRE GROSAM</title>
            <link>https://hudoc.echr.coe.int/eng?i=001-218240</link>
            <description>Chamber Judgment</description>
        </item>
    </channel>
</rss>
""",
        encoding="utf-8",
    )
    subsite, items = parse_rss_file(rss_file)
    assert subsite == "echr"
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-218240"
    assert items[0]["title"] == "AFFAIRE GROSAM"


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
    mock_item.find.side_effect = lambda tag: (
        None if tag == "link" else MagicMock(text="test")
    )
    mock_root = MagicMock()
    mock_root.findall.return_value = [
        MagicMock(
            find=lambda tag: (
                MagicMock(text='https://hudoc.echr.coe.int/eng#{"itemid":["test"]}')
                if tag == "link"
                else MagicMock(text="test")
            )
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
            elem.text = 'https://hudoc.echr.coe.int/eng#{"itemid":["test"]}'
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
            'Failed to parse pubDate: Invalid date value or format "invalid date"'
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
    """limit=0 takes every item; one thread fetches them in turn, pausing between."""
    items = [{"doc_id": "1"}, {"doc_id": "2"}, {"doc_id": "3"}]
    with (
        patch("hudoc.core.processor.parse_rss_file", return_value=("echr", items)),
        patch("hudoc.core.processor.download_document") as mock_download,
        patch("hudoc.core.processor.time.sleep") as mock_sleep,
    ):
        process_rss("rss.xml", "output", limit=0)
    assert mock_download.call_count == 3
    assert [c.args for c in mock_sleep.call_args_list] == [(3.0,), (3.0,)]


def test_process_rss_threads_use_executor():
    items = [{"doc_id": "1"}, {"doc_id": "2"}]
    with (
        patch("hudoc.core.processor.parse_rss_file", return_value=("echr", items)),
        patch("hudoc.core.processor.ThreadPoolExecutor") as mock_executor,
    ):
        process_rss("rss.xml", "output", limit=0, threads=2)
        assert mock_executor().__enter__().submit.call_count == 2


PDF_URL = (
    "https://hudoc.echr.coe.int/app/conversion/pdf/"
    "?library=ECHR&id={0}&filename={0}.pdf"
)


def test_process_rss_pdf_downloads_and_prints_evid_lines(tmp_path, fake_http, capsys):
    items = [{"doc_id": "001-253219"}, {"doc_id": "001-57619"}]
    fake_http.add(PDF_URL.format("001-253219"), content=b"%PDF-1.7 judgment")
    with (
        patch("hudoc.core.processor.parse_rss_file", return_value=("echr", items)),
        patch("hudoc.core.processor.download_document") as mock_download,
    ):
        lines = process_rss("rss.xml", tmp_path, limit=1, pdf=True, evid_set="coe")
    mock_download.assert_not_called()
    saved = tmp_path / "echr_001-253219.pdf"
    assert saved.read_bytes() == b"%PDF-1.7 judgment"
    assert lines == [f'evid --db evid doc add -s coe "{saved}"']
    assert capsys.readouterr().out.strip() == lines[0]
    assert fake_http.history == [PDF_URL.format("001-253219")]


def test_download_pdfs_pauses_between_fetches_and_keeps_existing(tmp_path, fake_http):
    from hudoc.core.processor import download_pdfs

    (tmp_path / "echr_001-1.pdf").write_bytes(b"%PDF old")
    for doc_id in ("001-2", "001-3"):
        fake_http.add(PDF_URL.format(doc_id), content=b"%PDF new")
    items = [{"doc_id": d} for d in ("001-1", "001-2", "001-3")]
    with patch("hudoc.core.processor.time.sleep") as mock_sleep:
        paths = download_pdfs("echr", items, tmp_path, delay=3.0)
    assert [p.name for p in paths] == ["echr_001-1.pdf", "echr_001-2.pdf", "echr_001-3.pdf"]
    assert (tmp_path / "echr_001-1.pdf").read_bytes() == b"%PDF old"
    assert fake_http.history == [PDF_URL.format("001-2"), PDF_URL.format("001-3")]
    assert [c.args for c in mock_sleep.call_args_list] == [(3.0,)]


def test_get_document_pdf_refuses_204_and_non_pdf(tmp_path, fake_http, caplog):
    from hudoc.fetcher import get_document_pdf

    fake_http.add("https://x/none", status_code=204)
    fake_http.add("https://x/page", text="<html>Just a moment...</html>")
    fake_http.add("https://x/denied", status_code=403, text="<html>challenge</html>")
    assert get_document_pdf("https://x/none", tmp_path / "a.pdf") is None
    assert get_document_pdf("https://x/page", tmp_path / "b.pdf") is None
    assert get_document_pdf("https://x/denied", tmp_path / "c.pdf") is None
    assert list(tmp_path.iterdir()) == []
    assert "check the item id" in caplog.text
    assert "Not a PDF" in caplog.text
    assert "HTTP 403" in caplog.text


def test_http_get_uses_curl(tmp_path):
    """A real round trip through the curl binary to a local server."""
    import functools
    import shutil
    import threading
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    import pytest

    from hudoc.fetcher import http_get

    if not shutil.which("curl"):
        pytest.skip("curl not installed")
    (tmp_path / "j.pdf").write_bytes(b"%PDF-1.4 body")
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(tmp_path))
    handler.log_message = lambda *a: None
    server = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        ok = http_get(f"{base}/j.pdf")
        missing = http_get(f"{base}/nope.pdf")
    finally:
        server.shutdown()
    assert (ok.status, ok.content) == (200, b"%PDF-1.4 body")
    assert missing.status == 404 and not missing.ok
    down = http_get(f"{base}/j.pdf", timeout=2)
    assert down.status == 0 and down.error


def test_http_get_without_curl(monkeypatch):
    from hudoc.fetcher import http_get

    monkeypatch.setattr("hudoc.fetcher.shutil.which", lambda name: None)
    response = http_get("https://example.com")
    assert response.status == 0 and response.error == "curl not found on PATH"


def test_pdf_url_quotes_the_id():
    from hudoc.core.constants import pdf_url

    assert pdf_url("grevio", "A/B 1") == (
        "https://hudoc.grevio.coe.int/app/conversion/pdf/"
        "?library=GREVIO&id=A%2FB%201&filename=A%2FB%201.pdf"
    )


def test_process_rss_echr(tmp_path, fake_http):
    """Test processing an ECHR RSS file with pre-downloaded content."""
    rss_file = Path("tests/data/echr_rss.xml")
    doc_id = "001-123456"
    output_dir = tmp_path / "output"

    with open("tests/data/echr_doc.html") as f:
        html_content = f.read()
    fake_http.add(
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


def test_parse_rss_url_success(fake_http):
    """Test parse_rss_url with a valid RSS response."""
    url = "https://hudoc.echr.coe.int/app/rss/?library=ECHR"
    xml = """<rss version="2.0"><channel>
        <item>
            <title>Test Case</title>
            <link>http://hudoc.echr.coe.int/eng#{"itemid":["001-999"]}</link>
            <description>Test Desc</description>
            <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
        </item>
    </channel></rss>"""
    fake_http.add(url, text=xml)
    subsite, items = parse_rss_url(url)
    assert subsite == "echr"
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-999"
    assert items[0]["title"] == "Test Case"


def test_parse_rss_url_request_error(fake_http):
    """Test parse_rss_url when HTTP request fails."""
    url = "https://hudoc.echr.coe.int/app/rss/?library=ECHR"
    fake_http.add(url, exc="connection refused")
    with patch("hudoc.core.parser.logging") as mock_logging:
        subsite, items = parse_rss_url(url)
    assert subsite is None
    assert items == []
    assert "Failed to fetch RSS" in mock_logging.error.call_args[0][0]


def test_parse_rss_url_no_items(fake_http):
    """Test parse_rss_url when RSS has no items."""
    url = "https://hudoc.echr.coe.int/app/rss/?library=ECHR"
    fake_http.add(url, text="<rss><channel></channel></rss>")
    with patch("hudoc.core.parser.logging") as mock_logging:
        subsite, items = parse_rss_url(url)
    assert subsite is None
    assert items == []
    mock_logging.warning.assert_called_with("No items found in RSS feed")


def test_process_rss_url_no_subsite():
    """Test process_rss_url when no subsite detected."""
    with (
        patch("hudoc.core.processor.parse_rss_url", return_value=(None, [])),
        patch("hudoc.core.processor.logging") as mock_logging,
    ):
        process_rss_url("https://example.com/rss", "output")
        mock_logging.error.assert_called_with("Failed to detect subsite or parse items")


def test_process_rss_url_no_items():
    """Test process_rss_url when no items."""
    with (
        patch("hudoc.core.processor.parse_rss_url", return_value=("echr", [])),
        patch("hudoc.core.processor.logging") as mock_logging,
    ):
        process_rss_url("https://example.com/rss", "output")
        mock_logging.error.assert_called_with("No items to process")


def test_download_document_no_text():
    """Test download_document when no text is retrieved."""
    item = {"doc_id": "test", "title": "Test", "description": "Test"}
    with (
        patch("hudoc.core.processor.get_document_text", return_value=None),
        patch("hudoc.core.processor.logging") as mock_logging,
    ):
        download_document(item, "echr", "output", 2.0, False)
        mock_logging.warning.assert_called_with("No content retrieved for test")
