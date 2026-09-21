"""
Export a Deck to CSV, JSON, or Anki (.apkg) format.
"""
import csv
import json
from pathlib import Path

from app.card_management.deck_builder import Deck


def export_json(deck: Deck, output_path: str) -> Path:
    path = Path(output_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"name": deck.name, "cards": [c.to_dict() for c in deck.cards]},
            f,
            indent=2,
        )
    return path


def export_csv(deck: Deck, output_path: str) -> Path:
    path = Path(output_path)
    fieldnames = [
        "id", "type", "prompt", "answer", "distractors",
        "difficulty", "question_type", "topic",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for card in deck.cards:
            row = card.to_dict()
            row["distractors"] = "; ".join(row["distractors"])
            writer.writerow({k: row[k] for k in fieldnames})
    return path


def export_anki(deck: Deck, output_path: str) -> Path:
    """
    Export to Anki's .apkg format using genanki.
    Flashcards use a basic front/back note type; MCQs are flattened into
    a question + answer-with-options note.
    """
    import genanki

    model = genanki.Model(
        1607392319,
        "Flashcard Generator Model",
        fields=[{"name": "Question"}, {"name": "Answer"}],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            }
        ],
    )

    anki_deck = genanki.Deck(2059400110, deck.name)

    for card in deck.cards:
        if card.type == "mcq" and card.distractors:
            options = card.distractors + [card.answer]
            options_html = "<br>".join(f"- {o}" for o in options)
            question = f"{card.prompt}<br><br>{options_html}"
        else:
            question = card.prompt

        anki_deck.add_note(genanki.Note(model=model, fields=[question, card.answer]))

    path = Path(output_path)
    genanki.Package(anki_deck).write_to_file(str(path))
    return path