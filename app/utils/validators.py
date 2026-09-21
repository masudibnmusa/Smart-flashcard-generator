"""
Checks generated cards aren't duplicate, malformed, or otherwise low
quality before they're committed to a deck.
"""
import difflib
from typing import List

from app.card_management.card_model import Card

REQUIRED_FIELDS = ("prompt", "answer")
SIMILARITY_THRESHOLD = 0.85  # prompts more similar than this are treated as duplicates


def is_malformed(card: Card) -> bool:
    """A card is malformed if required fields are empty, or an MCQ lacks
    a proper set of distractors."""
    for field_name in REQUIRED_FIELDS:
        value = getattr(card, field_name, "")
        if not value or not value.strip():
            return True

    if card.type == "mcq":
        if len(card.distractors) < 2:
            return True
        if card.answer.strip() in [d.strip() for d in card.distractors]:
            return True  # answer duplicated as a distractor

    return False


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def find_duplicates(cards: List[Card]) -> List[int]:
    """
    Return indices of cards considered near-duplicates of an earlier card
    in the list (based on prompt text similarity). This catches exact and
    near-exact repeats; semantically-equivalent-but-differently-worded
    duplicates would need embedding-based comparison, not implemented here.
    """
    duplicate_indices = []
    seen: List[str] = []
    for i, card in enumerate(cards):
        is_dup = any(_similarity(card.prompt, s) >= SIMILARITY_THRESHOLD for s in seen)
        if is_dup:
            duplicate_indices.append(i)
        else:
            seen.append(card.prompt)
    return duplicate_indices


def validate_cards(cards: List[Card]) -> List[Card]:
    """Filter a list of cards down to well-formed, non-duplicate ones."""
    well_formed = [c for c in cards if not is_malformed(c)]
    dup_indices = set(find_duplicates(well_formed))
    return [c for i, c in enumerate(well_formed) if i not in dup_indices]