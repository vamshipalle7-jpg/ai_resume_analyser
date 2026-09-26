import os
import pytest
from app.services.extractor import document_extractor

PDF_PATH = "tests/assets/sample_backend_developer.pdf"
DOCX_PATH = "tests/assets/sample_frontend_developer.docx"


def test_pdf_extraction():
    assert os.path.exists(PDF_PATH), f"Missing test file {PDF_PATH}"
    with open(PDF_PATH, "rb") as f:
        file_bytes = f.read()

    result = document_extractor.parse_document(file_bytes, "sample_backend_developer.pdf")
    assert result["file_type"] == "pdf"
    assert "Alex Mercer" in result["raw_text"]
    assert "alex.mercer@email.com" in result["raw_text"]
    assert result["contact_info"]["email"] == "alex.mercer@email.com"
    assert result["word_count"] > 100
    assert "FastAPI" in result["raw_text"]
    assert "PostgreSQL" in result["raw_text"]


def test_docx_extraction():
    assert os.path.exists(DOCX_PATH), f"Missing test file {DOCX_PATH}"
    with open(DOCX_PATH, "rb") as f:
        file_bytes = f.read()

    result = document_extractor.parse_document(file_bytes, "sample_frontend_developer.docx")
    assert result["file_type"] == "docx"
    assert "Elena Rostova" in result["raw_text"]
    assert "React.js" in result["raw_text"]
    assert "TypeScript" in result["raw_text"]
    assert result["contact_info"]["email"] == "elena.rostova@example.com"
    assert result["word_count"] > 80


def test_contact_info_parser():
    sample_text = """
    Jane Doe
    jane.doe@techcorp.io
    Phone: (415) 555-0199
    https://linkedin.com/in/janedoe
    https://github.com/janedoe-dev
    """
    contact = document_extractor.extract_contact_info(sample_text)
    assert contact["email"] == "jane.doe@techcorp.io"
    assert "555-0199" in contact["phone"]
    assert "linkedin.com/in/janedoe" in contact["linkedin"]
    assert "github.com/janedoe-dev" in contact["github"]
