"""
Parses PDF / DOCX / TXT / pasted text into a single plain-text string
ready for chunking.
"""
from pathlib import Path

import pdfplumber
from docx import Document


class UnsupportedFileTypeError(Exception):
    pass


def load_text(source: str, is_path: bool = True) -> str:
    """
    Load raw text from a file path or from pasted text.

    Args:
        source: file path OR raw pasted text
        is_path: if False, `source` is treated as already-loaded text

    Returns:
        Extracted plain text.
    """
    if not is_path:
        return source.strip()

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {source}")

    suffix = path.suffix.lower()
    if suffix == ".txt" or suffix == ".md":
        return _load_txt(path)
    elif suffix == ".pdf":
        return _load_pdf(path)
    elif suffix == ".docx":
        return _load_docx(path)
    else:
        raise UnsupportedFileTypeError(f"Unsupported file type: {suffix}")


def _load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _load_pdf(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    text = "\n\n".join(text_parts).strip()

    if not text:
        raise ValueError(
            "No extractable text found in PDF. It may be a scanned/image-based "
            "PDF — OCR support is not yet implemented."
        )
    return text


def _load_docx(path: Path) -> str:
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs).strip()