"""
Generates flashcards or MCQs from extracted concepts.
"""
import json
import uuid
from typing import List

from app.card_management.card_model import Card
from app.generation.concept_extractor import Concept
from app.generation.llm import llm_client
from app.generation.prompt_templates import (
    FLASHCARD_GENERATION_PROMPT,
    MCQ_GENERATION_PROMPT,
    QUESTION_GENERATION_SYSTEM,
)


def _concepts_to_json(concepts: List[Concept]) -> str:
    return json.dumps(
        [{"concept": c.concept, "fact": c.fact, "type": c.type} for c in concepts],
        indent=2,
    )


def generate_flashcards(
    concepts: List[Concept],
    question_count: int = 5,
    difficulty_mix: str = "easy:2,medium:2,hard:1",
    topic: str = "General",
) -> List[Card]:
    """Generate flashcard-style (front/back) cards from a list of concepts."""
    prompt = FLASHCARD_GENERATION_PROMPT.format(
        concepts_json=_concepts_to_json(concepts),
        question_count=question_count,
        difficulty_mix=difficulty_mix,
    )
    raw_cards = llm_client.complete_json(QUESTION_GENERATION_SYSTEM, prompt)
    return _to_cards(raw_cards, card_type="flashcard", topic=topic)


def generate_mcqs(
    concepts: List[Concept],
    question_count: int = 5,
    difficulty_mix: str = "easy:2,medium:2,hard:1",
    topic: str = "General",
) -> List[Card]:
    """Generate multiple-choice questions from a list of concepts."""
    prompt = MCQ_GENERATION_PROMPT.format(
        concepts_json=_concepts_to_json(concepts),
        question_count=question_count,
        difficulty_mix=difficulty_mix,
    )
    raw_cards = llm_client.complete_json(QUESTION_GENERATION_SYSTEM, prompt)
    return _to_cards(raw_cards, card_type="mcq", topic=topic)


def _to_cards(raw_cards: list, card_type: str, topic: str) -> List[Card]:
    cards = []
    for item in raw_cards:
        try:
            cards.append(
                Card(
                    id=f"card_{uuid.uuid4().hex[:8]}",
                    type=card_type,
                    prompt=item["prompt"],
                    answer=item["answer"],
                    distractors=item.get("distractors", []),
                    difficulty=item.get("difficulty", "medium"),
                    question_type=item.get("question_type", "definition"),
                    topic=topic,
                    source_concept=item.get("source_concept", ""),
                )
            )
        except KeyError:
            continue  # skip malformed entries rather than failing the whole batch

    return cards