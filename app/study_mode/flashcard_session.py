"""
Flip-card review logic for flashcard-mode study sessions.
"""
import random
from dataclasses import dataclass, field
from typing import List, Optional

from app.card_management.card_model import Card


@dataclass
class FlashcardSession:
    cards: List[Card]
    shuffle: bool = True
    _index: int = field(default=0, init=False)
    _results: dict = field(default_factory=dict, init=False)  # card_id -> bool

    def __post_init__(self):
        if self.shuffle:
            random.shuffle(self.cards)

    @property
    def current_card(self) -> Optional[Card]:
        if self._index >= len(self.cards):
            return None
        return self.cards[self._index]

    @property
    def progress(self) -> str:
        return f"{min(self._index + 1, len(self.cards))}/{len(self.cards)}"

    def mark(self, remembered: bool) -> None:
        """Record whether the current card was remembered, then advance."""
        card = self.current_card
        if card is None:
            return
        card.record_result(remembered)
        self._results[card.id] = remembered
        self._index += 1

    def is_complete(self) -> bool:
        return self._index >= len(self.cards)

    def summary(self) -> dict:
        total = len(self._results)
        correct = sum(1 for v in self._results.values() if v)
        return {
            "total_reviewed": total,
            "remembered": correct,
            "missed": total - correct,
            "accuracy": round(correct / total, 2) if total else 0.0,
        }

    def missed_cards(self) -> List[Card]:
        return [c for c in self.cards if self._results.get(c.id) is False]