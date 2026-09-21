"""
Unified data model for both flashcards and MCQs. Keeping one schema for
both types keeps deck_builder.py and exporter.py simple.
"""
from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class Card:
    id: str
    type: str                      # "flashcard" | "mcq"
    prompt: str
    answer: str
    distractors: List[str] = field(default_factory=list)  # populated only for mcq
    difficulty: str = "medium"     # "easy" | "medium" | "hard"
    question_type: str = "definition"  # "definition" | "application" | "comparison"
    topic: str = "General"
    source_concept: str = ""
    source_chunk_id: str = ""

    # SRS state (used by spaced_repetition.py)
    box: int = 1
    times_seen: int = 0
    times_correct: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        return cls(**data)

    def record_result(self, correct: bool) -> None:
        self.times_seen += 1
        if correct:
            self.times_correct += 1