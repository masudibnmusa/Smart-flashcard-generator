"""
Pulls key facts, definitions, and concepts out of each chunk of source
material before question generation happens. Keeping this as a separate
stage gives us a clean, auditable intermediate representation.
"""
from dataclasses import dataclass
from typing import List

from app.generation.llm import llm_client
from app.generation.prompt_templates import (
    CONCEPT_EXTRACTION_PROMPT,
    CONCEPT_EXTRACTION_SYSTEM,
)
from app.ingestion.chunker import Chunk


@dataclass
class Concept:
    concept: str
    fact: str
    type: str
    chunk_id: str


def extract_concepts(chunk: Chunk, max_concepts: int = 8) -> List[Concept]:
    """Extract key concepts from a single chunk."""
    prompt = CONCEPT_EXTRACTION_PROMPT.format(
        max_concepts=max_concepts, chunk_text=chunk.text
    )
    raw_concepts = llm_client.complete_json(CONCEPT_EXTRACTION_SYSTEM, prompt)

    concepts = []
    for item in raw_concepts:
        try:
            concepts.append(
                Concept(
                    concept=item["concept"],
                    fact=item["fact"],
                    type=item.get("type", "fact"),
                    chunk_id=chunk.id,
                )
            )
        except KeyError:
            continue  # skip malformed entries rather than failing the whole batch

    return concepts


def extract_concepts_for_chunks(chunks: List[Chunk], max_concepts: int = 8) -> List[Concept]:
    """Extract concepts across all chunks of a document."""
    all_concepts = []
    for chunk in chunks:
        all_concepts.extend(extract_concepts(chunk, max_concepts=max_concepts))
    return all_concepts