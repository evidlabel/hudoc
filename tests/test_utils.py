import uuid

import yaml

from hudoc.utils import (
    get_document_text,
    save_text,
    trigger_document_conversion,
    clean_text_for_typst,
    typst_dict,
)


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
    assert not any(req.url == rss_link for req in requests_mock.request_history), (
        "Conversion should not be triggered"
    )


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


def test_trigger_document_conversion_no_link():
    """Test trigger_document_conversion with no RSS link."""
    assert not trigger_document_conversion(None, "test")


def test_trigger_document_conversion_failure(requests_mock):
    """Test trigger_document_conversion failure."""
    rss_link = "https://example.com"
    requests_mock.get(rss_link, status_code=500)
    assert not trigger_document_conversion(rss_link, "test")


def test_clean_text_for_typst():
    """Test clean_text_for_typst function."""
    text = 'Test # * _ ~ ^ ` " $ < > \n\n'
    cleaned = clean_text_for_typst(text)
    assert cleaned == 'Test \\# \\* \\_ \\~ \\^ \\` \\" \\$ \\< \\>\n\n'


def test_typst_dict():
    """Test typst_dict conversion."""
    d = {"key": 'value "escaped"', "list": ["item1", "item2"], "num": 42}
    result = typst_dict(d)
    assert 'key: "value "escaped""' in result
    assert 'list: ("item1", "item2")' in result
    assert "num: 42" in result


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


def test_save_evid_echr(tmp_path, monkeypatch):
    """Test saving an ECHR document in evid format."""
    output_dir = tmp_path / "output"
    text = "Test content with special chars: # % &"
    doc_id = "001-123456"
    title = "Test Case"
    filename = "echr_doc_001-123456.txt"

    # Mock UUID to ensure predictable subdirectory
    fixed_uuid = "123e4567-e89b-12d3-a456-426614174000"
    monkeypatch.setattr(uuid, "uuid5", lambda ns, name: uuid.UUID(fixed_uuid))

    save_text(text, doc_id, title, None, output_dir, "echr", evid=True)

    subdir_path = output_dir / fixed_uuid
    typst_file = subdir_path / "label.typ"
    yaml_file = subdir_path / "info.yml"

    assert typst_file.exists()
    assert yaml_file.exists()

    typst_content = typst_file.read_text(encoding="utf-8")
    assert "Test content with special chars: \\# % &" in typst_content

    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
    assert yaml_content["label"] == "No description"
    assert yaml_content["original_name"] == filename
    assert yaml_content["uuid"] == fixed_uuid
    assert yaml_content["title"] == "Test Case"


def test_save_text_oserror(tmp_path, monkeypatch):
    """Test save_text with OSError."""
    output_dir = tmp_path / "output"
    monkeypatch.setattr("builtins.open", side_effect=OSError("Test error"))
    save_text("text", "doc_id", "title", None, output_dir, "echr")
    # Check logging error
