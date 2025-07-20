from pathlib import Path

from hudoc.core.parser import parse_rss_file
from hudoc.core.processor import process_rss


def test_parse_rss_file_echr():
    """Test parsing an ECHR RSS file."""
    rss_file = Path("tests/data/echr_rss.xml")
    subsite, items = parse_rss_file(rss_file)  # Fixed to call with one argument
    assert subsite == "echr"  # Assuming subsite detection
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-123456"
    assert items[0]["title"] == "CASE OF TEST v. TEST"
    assert items[0]["description"] == "12345/20 - Chamber Judgment"


def test_parse_rss_file_grevio():
    """Test parsing a GREVIO RSS file."""
    rss_file = Path("tests/data/grevio_rss.xml")
    subsite, items = parse_rss_file(rss_file)  # Fixed to call with one argument
    assert subsite == "grevio"  # Assuming subsite detection
    assert len(items) == 1
    assert items[0]["doc_id"] == "TEST-2023-1"
    assert items[0]["title"] == "Test Report"
    assert items[0]["description"] == "Test Description"


def test_process_rss_echr(tmp_path, requests_mock):
    """Test processing an ECHR RSS file with pre-downloaded content."""
    rss_file = Path("tests/data/echr_rss.xml")
    doc_id = "001-123456"
    output_dir = tmp_path / "output"

    # Mock HTTP request to return pre-downloaded HTML
    with open("tests/data/echr_doc.html") as f:
        html_content = f.read()
    requests_mock.get(
        f"https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id={doc_id}",
        text=html_content,
    )

    process_rss(  # Fixed to call with correct arguments
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
