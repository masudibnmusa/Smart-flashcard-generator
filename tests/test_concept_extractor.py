from unittest.mock import patch

from app.generation.concept_extractor import Concept, extract_concepts
from app.ingestion.chunker import Chunk

MOCK_RESPONSE = [
    {
        "concept": "Mitochondria",
        "fact": "The mitochondrion is the powerhouse of the cell.",
        "type": "definition",
    },
    {
        "concept": "Missing field example",
        # intentionally missing "fact" to test malformed handling
    },
]


@patch("app.generation.concept_extractor.llm_client")
def test_extract_concepts_parses_valid_entries(mock_client):
    mock_client.complete_json.return_value = MOCK_RESPONSE
    chunk = Chunk(id="chunk_0001", text="Some biology text about cells.")

    concepts = extract_concepts(chunk, max_concepts=5)

    assert len(concepts) == 1  # malformed entry should be skipped
    assert isinstance(concepts[0], Concept)
    assert concepts[0].concept == "Mitochondria"
    assert concepts[0].chunk_id == "chunk_0001"


@patch("app.generation.concept_extractor.llm_client")
def test_extract_concepts_empty_response(mock_client):
    mock_client.complete_json.return_value = []
    chunk = Chunk(id="chunk_0002", text="Empty section.")

    concepts = extract_concepts(chunk)

    assert concepts == []