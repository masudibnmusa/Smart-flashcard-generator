"""
Simple Leitner-system spaced repetition.

Boxes 1-5, each with an increasing review interval. Correct answers move
a card up a box (reviewed less often); incorrect answers send it back to
box 1 (reviewed again soon). State is tracked on the Card itself
(card.box) and logged to data/study_history/ for persistence.
"""
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from app.card_management.card_model import Card
from app.config import config

# Days until a card in each box is due for review again.
BOX_INTERVALS_DAYS = {1: 0, 2: 1, 3: 3, 4: 7, 5: 14}
MAX_BOX = max(BOX_INTERVALS_DAYS)


@dataclass
class ReviewRecord:
    card_id: str
    box: int
    last_reviewed: str  # ISO timestamp
    next_due: str        # ISO timestamp


class LeitnerSystem:
    def __init__(self, deck_name: str, history_dir: str | None = None):
        self.deck_name = deck_name
        self.history_dir = Path(history_dir or config.study_history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, ReviewRecord] = self._load()

    def review(self, card: Card, correct: bool) -> None:
        """Update a card's box based on whether it was answered correctly."""
        if correct:
            card.box = min(card.box + 1, MAX_BOX)
        else:
            card.box = 1

        now = datetime.utcnow()
        due = now + timedelta(days=BOX_INTERVALS_DAYS[card.box])
        self._records[card.id] = ReviewRecord(
            card_id=card.id,
            box=card.box,
            last_reviewed=now.isoformat(),
            next_due=due.isoformat(),
        )
        self._save()

    def due_cards(self, cards: List[Card]) -> List[Card]:
        """Return the subset of cards that are due for review now."""
        now = datetime.utcnow()
        due = []
        for card in cards:
            record = self._records.get(card.id)
            if record is None:
                due.append(card)  # never reviewed -> due immediately
                continue
            if datetime.fromisoformat(record.next_due) <= now:
                due.append(card)
        return due

    def _history_path(self) -> Path:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in self.deck_name)
        return self.history_dir / f"{safe_name}_srs.json"

    def _load(self) -> dict[str, ReviewRecord]:
        path = self._history_path()
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k: ReviewRecord(**v) for k, v in raw.items()}

    def _save(self) -> None:
        path = self._history_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({k: vars(v) for k, v in self._records.items()}, f, indent=2)