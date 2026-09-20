"""
Central configuration for the flashcard generator.
Reads from environment variables (see .env.example).
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # LLM
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "claude-sonnet-4-6"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("MAX_TOKENS", "2000")))

    # Chunking
    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100")))

    # Generation
    questions_per_chunk: int = field(default_factory=lambda: int(os.getenv("QUESTIONS_PER_CHUNK", "5")))
    difficulty_mix: str = field(default_factory=lambda: os.getenv("DEFAULT_DIFFICULTY_MIX", "easy:2,medium:2,hard:1"))

    # Paths
    source_material_dir: str = "data/source_material"
    decks_dir: str = "data/decks"
    study_history_dir: str = "data/study_history"

    def validate(self) -> None:
        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
            )


config = Config()