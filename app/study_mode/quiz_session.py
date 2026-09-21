"""
MCQ scoring logic for quiz-mode study sessions.
"""
import random
from dataclasses import dataclass, field
from typing import List, Optional

from app.card_management.card_model import Card


@dataclass
class QuizSession:
    cards: List[Card]
    shuffle: bool = True
    shuffle_options: bool = True
    _index: int = field(default=0, init=False)
    _results: dict = field(default_factory=dict, init=False)  # card_id -> bool
    _option_cache: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        if self.shuffle:
            random.shuffle(self.cards)

    @property
    def current_card(self) -> Optional[Card]:
        if self._index >= len(self.cards):
            return None
        return self.cards[self._index]

    def current_options(self) -> List[str]:
        """Return the answer + distractors, shuffled and cached per card."""
        card = self.current_card
        if card is None:
            return []
        if card.id not in self._option_cache:
            options = [card.answer] + list(card.distractors)
            if self.shuffle_options:
                random.shuffle(options)
            self._option_cache[card.id] = options
        return self._option_cache[card.id]

    def submit_answer(self, selected_option: str) -> bool:
        """Submit an answer for the current card, record result, advance."""
        card = self.current_card
        if card is None:
            return False
        correct = selected_option.strip() == card.answer.strip()
        card.record_result(correct)
        self._results[card.id] = correct
        self._index += 1
        return correct

    def is_complete(self) -> bool:
        return self._index >= len(self.cards)

    def score(self) -> dict:
        total = len(self._results)
        correct = sum(1 for v in self._results.values() if v)
        return {
            "total_questions": total,
            "correct": correct,
            "incorrect": total - correct,
            "percentage": round((correct / total) * 100, 1) if total else 0.0,
        }

    def missed_cards(self) -> List[Card]:
        return [c for c in self.cards if self._results.get(c.id) is False]