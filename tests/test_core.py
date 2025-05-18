from pathlib import Path

import pytest

from hudoc.core.parser import parse_link, parse_rss_file
from hudoc.core.processor import process_link, process_rss


def test_parse_rss_file_echr():
    """Test parsing an ECHR RSS file."""
    rss_file = Path("tests/data/echr_rss.xml")
    items = parse_rss_file(rss_file, "echr")
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-123456"
    assert items[0]["title"] == "CASE OF TEST v. TEST"
    assert items[0]["description"] is None


def test_parse_rss_file_grevio():
    """Test parsing a GREVIO RSS file."""
    rss_file = Path("tests/data/grevio_rss.xml")
    items = parse_rss_file(rss_file, "grevio")
    assert len(items) == 1
    assert items[0]["doc_id"] == "TEST-2023-1"
    assert items[0]["title"] == "Test Report"
    assert items[0]["description"] == "Test Description"


def test_parse_link_echr():
    """Test parsing an ECHR document link."""
    link = 'http://hudoc.echr.coe.int/eng#{"itemid":["001-123456"]}'
    items = parse_link(link, "echr")
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-123456"
    assert items[0]["title"] == "Untitled"


def test_parse_link_grevio():
    """Test parsing a GREVIO document link."""
    link = 'http://hudoc.grevio.coe.int/eng#{"greviosectionid":["TEST-2023-1"]}'
    items = parse_link(link, "grevio")
    assert len(items) == 1
    assert items[0]["doc_id"] == "TEST-2023-1"
    assert items[0]["title"] == "Untitled"


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

    process_rss("echr", rss_file, output_dir, full=False, threads=1)
    output_file = output_dir / f"echr_case_{doc_id}.txt"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Title: CASE OF TEST v. TEST" in content
    assert "ECHR Test Paragraph" in content


@pytest.mark.skip(reason="Skipping GREVIO test for now")
def test_process_link_grevio(tmp_path, requests_mock):
    """Test processing a GREVIO document link with pre-downloaded content."""
    link = 'http://hudoc.grevio.coe.int/eng#{"greviosectionid":["TEST-2023-1"]}'
    doc_id = "TEST-2023-1"
    output_dir = tmp_path / "output"

    # Mock HTTP request to return pre-downloaded HTML
    with open("tests/data/grevio_doc.html") as f:
        html_content = f.read()
    requests_mock.get(
        f"https://hudoc.grevio.coe.int/app/conversion/docx/html/body?library=GREVIO&id={doc_id}",
        text=html_content,
    )

    process_link("grevio", link, output_dir)
    output_file = output_dir / f"grevio_doc_{doc_id}.txt"
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Title: Untitled" in content
    assert "GREVIO Test Paragraph" in content
