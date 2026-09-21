from app.ingestion.chunker import chunk_by_heading, chunk_by_tokens, chunk_text


def test_chunk_by_heading_splits_on_headings():
    text = "# Intro\nSome intro text.\n# Section 2\nMore text here."
    sections = chunk_by_heading(text)
    assert len(sections) == 2
    assert sections[0].startswith("# Intro")
    assert sections[1].startswith("# Section 2")


def test_chunk_by_heading_no_headings_returns_whole_text():
    text = "Just a plain paragraph with no headings at all."
    sections = chunk_by_heading(text)
    assert sections == [text]


def test_chunk_by_tokens_respects_overlap():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_by_tokens(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    # Confirm overlap: last words of chunk 1 should appear in chunk 2
    last_words_chunk1 = chunks[0].split()[-5:]
    assert any(w in chunks[1] for w in last_words_chunk1)


def test_chunk_text_auto_assigns_ids_in_order():
    text = "# A\nText A.\n# B\nText B."
    chunks = chunk_text(text, strategy="heading")
    ids = [c.id for c in chunks]
    assert ids == sorted(ids)
    assert chunks[0].order == 0
    assert chunks[1].order == 1