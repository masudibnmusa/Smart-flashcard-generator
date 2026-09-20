"""
Splits raw text into digestible chunks for concept extraction.
Prefers splitting on markdown-style / textbook-style headings; falls back
to token-count-based splitting with overlap so context isn't severed
across chunk boundaries.
"""
import re
from dataclasses import dataclass, field
from typing import List

HEADING_PATTERN = re.compile(
    r"^(#{1,3}\s+.+|Chapter\s+\d+.*|Section\s+\d+(\.\d+)*.*|[A-Z][A-Za-z\s]{3,60}:?\s*$)",
    re.MULTILINE,
)


@dataclass
class Chunk:
    id: str
    text: str
    heading: str = ""
    order: int = 0
    metadata: dict = field(default_factory=dict)


def _estimate_tokens(text: str) -> int:
    # Rough heuristic: ~4 chars per token for English text.
    return max(1, len(text) // 4)


def chunk_by_heading(text: str) -> List[str]:
    """Split text into sections based on detected headings."""
    matches = list(HEADING_PATTERN.finditer(text))
    if not matches:
        return [text]

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)

    # Capture any preamble before the first heading.
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.insert(0, preamble)

    return sections


def chunk_by_tokens(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into ~chunk_size-token pieces with a sliding overlap window
    so a concept split across a boundary still has surrounding context.
    """
    words = text.split()
    words_per_chunk = chunk_size * 4 // 5  # rough token-to-word conversion
    overlap_words = overlap * 4 // 5

    if words_per_chunk <= 0:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + words_per_chunk
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start = end - overlap_words

    return chunks


def chunk_text(
    text: str,
    strategy: str = "auto",
    chunk_size: int = 1000,
    overlap: int = 100,
) -> List[Chunk]:
    """
    Main entry point. strategy: "heading" | "tokens" | "auto".
    "auto" tries heading-based splitting first and falls back to
    token-based splitting for any section still larger than chunk_size.
    """
    if strategy == "tokens":
        raw_sections = chunk_by_tokens(text, chunk_size, overlap)
    elif strategy == "heading":
        raw_sections = chunk_by_heading(text)
    else:  # auto
        heading_sections = chunk_by_heading(text)
        raw_sections = []
        for section in heading_sections:
            if _estimate_tokens(section) > chunk_size * 1.5:
                raw_sections.extend(chunk_by_tokens(section, chunk_size, overlap))
            else:
                raw_sections.append(section)

    chunks = []
    for i, section in enumerate(raw_sections):
        heading_match = HEADING_PATTERN.match(section)
        heading = heading_match.group(0).strip() if heading_match else ""
        chunks.append(
            Chunk(id=f"chunk_{i:04d}", text=section, heading=heading, order=i)
        )

    return chunks