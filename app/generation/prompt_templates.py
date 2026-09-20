"""
Prompt templates for concept extraction and question generation.
Kept separate from the calling logic so prompts can be iterated on
without touching pipeline code.
"""

CONCEPT_EXTRACTION_SYSTEM = """You are a study-material analyst. Given a section of \
notes or textbook text, extract the key facts, definitions, and concepts a student \
would need to know for an exam. Be precise and avoid trivial or overly obvious facts."""

CONCEPT_EXTRACTION_PROMPT = """Extract the key concepts from the following text.

Return ONLY a JSON array, no preamble, no markdown fences, in this exact shape:
[
  {{
    "concept": "short name of the concept",
    "fact": "the key fact or definition, stated clearly and completely",
    "type": "definition | fact | process | comparison | example"
  }}
]

Extract at most {max_concepts} of the most important concepts.

TEXT:
\"\"\"
{chunk_text}
\"\"\"
"""

QUESTION_GENERATION_SYSTEM = """You are an expert quiz writer creating study questions \
for students. Questions must be answerable strictly from the given facts, unambiguous, \
and free of trick wording. For multiple choice, distractors must be plausible but \
clearly wrong to someone who understands the material."""

FLASHCARD_GENERATION_PROMPT = """Given these key concepts, generate flashcards (front/back).

CONCEPTS:
{concepts_json}

Return ONLY a JSON array, no preamble, no markdown fences, in this exact shape:
[
  {{
    "prompt": "the question or term (front of card)",
    "answer": "the answer or definition (back of card)",
    "difficulty": "easy | medium | hard",
    "question_type": "definition | application | comparison",
    "source_concept": "which concept this came from"
  }}
]

Generate {question_count} flashcards total, roughly matching this difficulty mix: {difficulty_mix}.
"""

MCQ_GENERATION_PROMPT = """Given these key concepts, generate multiple-choice questions.

CONCEPTS:
{concepts_json}

Return ONLY a JSON array, no preamble, no markdown fences, in this exact shape:
[
  {{
    "prompt": "the question",
    "answer": "the correct answer",
    "distractors": ["wrong option 1", "wrong option 2", "wrong option 3"],
    "difficulty": "easy | medium | hard",
    "question_type": "definition | application | comparison",
    "source_concept": "which concept this came from"
  }}
]

Generate {question_count} MCQs total, roughly matching this difficulty mix: {difficulty_mix}.
Each question must have exactly 3 distractors, all plausible but unambiguously incorrect.
"""