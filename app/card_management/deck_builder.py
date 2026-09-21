"""
Organizes generated cards into decks, grouped by topic, and handles
persisting/loading decks to/from data/decks/*.json.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from app.card_management.card_model import Card
from app.config import config


@dataclass
class Deck:
    name: str
    cards: List[Card] = field(default_factory=list)

    def add_cards(self, cards: List[Card]) -> None:
        self.cards.extend(cards)

    def cards_by_topic(self) -> dict:
        grouped = {}
        for card in self.cards:
            grouped.setdefault(card.topic, []).append(card)
        return grouped

    def cards_by_difficulty(self, difficulty: str) -> List[Card]:
        return [c for c in self.cards if c.difficulty == difficulty]

    def save(self, directory: str | None = None) -> Path:
        directory = Path(directory or config.decks_dir)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self._safe_filename()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"name": self.name, "cards": [c.to_dict() for c in self.cards]},
                f,
                indent=2,
            )
        return path

    @classmethod
    def load(cls, path: str) -> "Deck":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cards = [Card.from_dict(c) for c in data["cards"]]
        return cls(name=data["name"], cards=cards)

    def _safe_filename(self) -> str:
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in self.name.lower())