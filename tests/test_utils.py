from hudoc.utils import get_document_text, save_text


def test_get_document_text(requests_mock):
    """Test extracting text from a mocked HUDOC document."""
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
        "test", "https://hudoc.echr.coe.int/app/conversion/docx/html/body", "ECHR"
    )
    expected = "Test paragraph 1\n\nTest heading\n\nTest paragraph 2"
    assert text == expected


def test_get_document_text_empty(requests_mock):
    """Test handling empty document content."""
    requests_mock.get(
        "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id=test",
        text="<html><body></body></html>",
    )

    text = get_document_text(
        "test", "https://hudoc.echr.coe.int/app/conversion/docx/html/body", "ECHR"
    )
    assert text is None


def test_save_text_echr(tmp_path):
    """Test saving an ECHR document to a file."""
    output_dir = tmp_path / "output"
    text = "Test content"
    doc_id = "001-123456"
    title = "Test Case"

    save_text(text, doc_id, title, None, output_dir, "echr")

    filepath = output_dir / "echr_case_001-123456.txt"
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
