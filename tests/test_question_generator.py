from unittest.mock import patch

from app.generation.concept_extractor import Concept
from app.generation.question_generator import generate_flashcards, generate_mcqs

MOCK_FLASHCARDS = [
    {
        "prompt": "What is the powerhouse of the cell?",
        "answer": "The mitochondrion",
        "difficulty": "easy",
        "question_type": "definition",
        "source_concept": "Mitochondria",
    }
]

MOCK_MCQS = [
    {
        "prompt": "What is the powerhouse of the cell?",
        "answer": "The mitochondrion",
        "distractors": ["The nucleus", "The ribosome", "The Golgi apparatus"],
        "difficulty": "easy",
        "question_type": "definition",
        "source_concept": "Mitochondria",
    }
]

SAMPLE_CONCEPTS = [
    Concept(concept="Mitochondria", fact="Powerhouse of the cell.", type="definition", chunk_id="chunk_0001")
]


@patch("app.generation.question_generator.llm_client")
def test_generate_flashcards(mock_client):
    mock_client.complete_json.return_value = MOCK_FLASHCARDS
    cards = generate_flashcards(SAMPLE_CONCEPTS, question_count=1, topic="Biology")

    assert len(cards) == 1
    assert cards[0].type == "flashcard"
    assert cards[0].topic == "Biology"
    assert cards[0].distractors == []


@patch("app.generation.question_generator.llm_client")
def test_generate_mcqs_includes_distractors(mock_client):
    mock_client.complete_json.return_value = MOCK_MCQS
    cards = generate_mcqs(SAMPLE_CONCEPTS, question_count=1, topic="Biology")

    assert len(cards) == 1
    assert cards[0].type == "mcq"
    assert len(cards[0].distractors) == 3


@patch("app.generation.question_generator.llm_client")
def test_generate_flashcards_skips_malformed(mock_client):
    mock_client.complete_json.return_value = [{"prompt": "Missing answer field"}]
    cards = generate_flashcards(SAMPLE_CONCEPTS, question_count=1)

    assert cards == []