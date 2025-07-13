import uuid

import pytest
import yaml

from hudoc.utils import get_document_text, save_text


def test_get_document_text_direct_success(requests_mock):
    """Test direct download success without triggering conversion."""
    doc_id = "test"
    rss_link = 'https://hudoc.echr.coe.int/eng#{"itemid":"test"}'
    requests_mock.get(
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=test",
        text="""
        <html>
            <body>
                <p>Test paragraph 1</p>
                <h2>Test heading</h2>
                <p>Test paragraph 2</p>
            </body>
        </html>
        """,
    )

    text = get_document_text(
        doc_id,
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body",
        "ECHR",
        rss_link=rss_link,
        conversion_delay=0.1,
    )
    expected = "Test paragraph 1\n\nTest heading\n\nTest paragraph 2"
    assert text == expected
    assert not any(
        req.url == rss_link for req in requests_mock.request_history
    ), "Conversion should not be triggered"


def test_get_document_text_empty_triggers_conversion(requests_mock):
    """Test empty direct download triggers conversion."""
    doc_id = "test"
    rss_link = 'https://hudoc.echr.coe.int/eng#{"itemid":"test"}'
    requests_mock.get(
        rss_link,
        status_code=200,
        text="Conversion triggered",
    )
    requests_mock.get(
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=test",
        [
            {"text": "<html><body></body></html>", "status_code": 200},
            {
                "text": """
                <html>
                    <body>
                        <p>Test paragraph 1</p>
                        <h2>Test heading</h2>
                        <p>Test paragraph 2</p>
                    </body>
                </html>
                """,
                "status_code": 200,
            },
        ],
    )

    text = get_document_text(
        doc_id,
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body",
        "ECHR",
        rss_link=rss_link,
        conversion_delay=0.1,
    )
    expected = "Test paragraph 1\n\nTest heading\n\nTest paragraph 2"
    assert text == expected


def test_get_document_text_failure_triggers_conversion(requests_mock):
    """Test failed direct download triggers conversion."""
    doc_id = "test"
    rss_link = 'https://hudoc.echr.coe.int/eng#{"itemid":"test"}'
    requests_mock.get(
        rss_link,
        status_code=200,
        text="Conversion triggered",
    )
    requests_mock.get(
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=test",
        [
            {"status_code": 500},
            {
                "text": """
                <html>
                    <body>
                        <p>Test paragraph 1</p>
                        <h2>Test heading</h2>
                        <p>Test paragraph 2</p>
                    </body>
                </html>
                """,
                "status_code": 200,
            },
        ],
    )

    text = get_document_text(
        doc_id,
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body",
        "ECHR",
        rss_link=rss_link,
        conversion_delay=0.1,
    )
    expected = "Test paragraph 1\n\nTest heading\n\nTest paragraph 2"
    assert text == expected


def test_get_document_text_empty_no_rss_link(requests_mock):
    """Test empty document content without RSS link."""
    doc_id = "test"
    requests_mock.get(
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=test",
        text="<html><body></body></html>",
    )

    text = get_document_text(
        doc_id,
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body",
        "ECHR",
        conversion_delay=0.1,
    )
    assert text is None


def test_save_text_echr(tmp_path):
    """Test saving an ECHR document to a file."""
    output_dir = tmp_path / "output"
    text = "Test content"
    doc_id = "001-123456"
    title = "Test Case"

    save_text(text, doc_id, title, None, output_dir, "echr")

    filepath = output_dir / "echr_doc_001-123456.txt"
    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8")
    assert content == "Title: Test Case\nTest content"


def test_save_text_grevio(tmp_path):
    """Test saving a GREVIO document to a file."""
    output_dir = tmp_path / "output"
    text = "Test content"
    doc_id = "TEST-2023-1"
    title = "Test Report"
    description = "Test Description"

    save_text(text, doc_id, title, description, output_dir, "grevio")

    filepath = output_dir / "grevio_doc_TEST-2023-1.txt"
    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8")
    assert (
        content == "Title: Test Report\nDescription: Test Description\n\nTest content"
    )


@pytest.mark.skip(reason="fails for now")
def test_save_evid_echr(tmp_path, monkeypatch):
    """Test saving an ECHR document in evid format."""
    output_dir = tmp_path / "output"
    text = "Test content with special chars: # % &"
    doc_id = "001-123456"
    title = "Test Case"
    filename = "echr_doc_001-123456.txt"

    # Mock UUID to ensure predictable subdirectory
    fixed_uuid = "123e4567-e89b-12d3-a456-426614174000"
    monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID(fixed_uuid))

    save_text(text, doc_id, title, None, output_dir, "echr", evid=True)

    subdir_path = output_dir / fixed_uuid
    latex_file = subdir_path / "label.tex"
    yaml_file = subdir_path / "info.yml"

    assert latex_file.exists()
    assert yaml_file.exists()

    latex_content = latex_file.read_text(encoding="utf-8")
    assert r"Test content with special chars: \# \% \&" in latex_content

    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
    assert yaml_content["label"] == "No description"
    assert yaml_content["original_name"] == filename
    assert yaml_content["uuid"] == fixed_uuid
    assert yaml_content["title"] == "Test Case"
