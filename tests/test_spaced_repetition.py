import shutil
import tempfile

import pytest

from app.card_management.card_model import Card
from app.study_mode.spaced_repetition import LeitnerSystem


@pytest.fixture
def temp_history_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.fixture
def sample_card():
    return Card(id="card_0001", type="flashcard", prompt="Q", answer="A")


def test_correct_answer_moves_card_up_a_box(temp_history_dir, sample_card):
    srs = LeitnerSystem("Test Deck", history_dir=temp_history_dir)
    assert sample_card.box == 1

    srs.review(sample_card, correct=True)
    assert sample_card.box == 2

    srs.review(sample_card, correct=True)
    assert sample_card.box == 3


def test_incorrect_answer_resets_to_box_one(temp_history_dir, sample_card):
    srs = LeitnerSystem("Test Deck", history_dir=temp_history_dir)
    srs.review(sample_card, correct=True)
    srs.review(sample_card, correct=True)
    assert sample_card.box == 3

    srs.review(sample_card, correct=False)
    assert sample_card.box == 1


def test_box_does_not_exceed_max(temp_history_dir, sample_card):
    srs = LeitnerSystem("Test Deck", history_dir=temp_history_dir)
    for _ in range(10):
        srs.review(sample_card, correct=True)
    assert sample_card.box == 5


def test_unreviewed_card_is_due(temp_history_dir, sample_card):
    srs = LeitnerSystem("Test Deck", history_dir=temp_history_dir)
    due = srs.due_cards([sample_card])
    assert sample_card in due


def test_history_persists_across_instances(temp_history_dir, sample_card):
    srs1 = LeitnerSystem("Test Deck", history_dir=temp_history_dir)
    srs1.review(sample_card, correct=True)

    srs2 = LeitnerSystem("Test Deck", history_dir=temp_history_dir)
    assert "card_0001" in srs2._records
    assert srs2._records["card_0001"].box == 2