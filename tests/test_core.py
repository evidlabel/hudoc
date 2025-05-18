import pytest
import requests_mock
from unittest.mock import patch
from pathlib import Path

from hudoc.core import parse_rss_file, parse_link, process_rss, process_link


@pytest.fixture
def sample_echr_rss():
    """Provide a sample ECHR RSS content."""
    return """
    <rss version="2.0">
        <channel>
            <item>
                <title>CASE OF TEST v. TEST</title>
                <link>http://hudoc.echr.coe.int/eng#{"itemid":["001-123456"]}</link>
                <description>12345/20 - Chamber Judgment</description>
            </item>
        </channel>
    </rss>
    """


@pytest.fixture
def sample_grevio_rss():
    """Provide a sample GREVIO RSS content."""
    return """
    <rss version="2.0">
        <channel>
            <item>
                <title>Test Report</title>
                <link>http://hudoc.grevio.coe.int/eng#{"greviosectionid":["TEST-2023-1"]}</link>
                <description>Test Description</description>
            </item>
        </channel>
    </rss>
    """


def test_parse_rss_file_echr(tmp_path, sample_echr_rss):
    """Test parsing an ECHR RSS file."""
    rss_file = tmp_path / "echr_rss.xml"
    rss_file.write_text(sample_echr_rss)

    items = parse_rss_file(rss_file, "echr")
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-123456"
    assert items[0]["title"] == "CASE OF TEST v. TEST"
    assert items[0]["description"] is None


def test_parse_rss_file_grevio(tmp_path, sample_grevio_rss):
    """Test parsing a GREVIO RSS file."""
    rss_file = tmp_path / "grevio_rss.xml"
    rss_file.write_text(sample_grevio_rss)

    items = parse_rss_file(rss_file, "grevio")
    assert len(items) == 1
    assert items[0]["doc_id"] == "TEST-2023-1"
    assert items[0]["title"] == "Test Report"
    assert items[0]["description"] == "Test Description"


def test_parse_link_echr():
    """Test parsing an ECHR document link."""
    link = "http://hudoc.echr.coe.int/eng#{\"itemid\":[\"001-123456\"]}"
    items = parse_link(link, "echr")
    assert len(items) == 1
    assert items[0]["doc_id"] == "001-123456"
    assert items[0]["title"] == "Untitled"


def test_parse_link_grevio():
    """Test parsing a GREVIO document link."""
    link = "http://hudoc.grevio.coe.int/eng#{\"greviosectionid\":[\"TEST-2023-1\"]}"
    items = parse_link(link, "grevio")
    assert len(items) == 1
    assert items[0]["doc_id"] == "TEST-2023-1"
    assert items[0]["title"] == "Untitled"


def test_process_rss_echr(tmp_path, sample_echr_rss, requests_mock):
    """Test processing an ECHR RSS file."""
    rss_file = tmp_path / "echr_rss.xml"
    rss_file.write_text(sample_echr_rss)

    # Mock HTTP request
    requests_mock.get(
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=001-123456",
        text="<p>Test content</p>"
    )

    output_dir = tmp_path / "output"
    with patch("hudoc.utils.save_text") as mock_save:
        process_rss("echr", rss_file, output_dir, full=False, threads=1)
        assert mock_save.called
        call_args = mock_save.call_args[0]
        assert call_args[0] == "Test content"
        assert call_args[1] == "001-123456"
        assert call_args[2] == "CASE OF TEST v. TEST"


def test_process_link_grevio(tmp_path, requests_mock):
    """Test processing a GREVIO document link."""
    link = "http://hudoc.grevio.coe.int/eng#{\"greviosectionid\":[\"TEST-2023-1\"]}"

    # Mock HTTP request
    requests_mock.get(
        "https://hudoc.grevio.coe.int/app/conversion/docx/html/body?library=GREVIO&id=TEST-2023-1",
        text="<p>Test content</p>"
    )

    output_dir = tmp_path / "output"
    with patch("hudoc.utils.save_text") as mock_save:
        process_link("grevio", link, output_dir)
        assert mock_save.called
        call_args = mock_save.call_args[0]
        assert call_args[0] == "Test content"
        assert call_args[1] == "TEST-2023-1"
        assert call_args[2] == "Untitled"
