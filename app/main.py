"""
Streamlit entry point. Ties together ingestion -> generation ->
card_management -> study_mode into a single-page app.

Run with: streamlit run app/main.py
"""
import streamlit as st

from app.card_management.deck_builder import Deck
from app.card_management.exporter import export_anki, export_csv, export_json
from app.config import config
from app.generation.concept_extractor import extract_concepts_for_chunks
from app.generation.question_generator import generate_flashcards, generate_mcqs
from app.ingestion.chunker import chunk_text
from app.ingestion.loader import load_text
from app.study_mode.flashcard_session import FlashcardSession
from app.study_mode.quiz_session import QuizSession
from app.utils.validators import validate_cards

st.set_page_config(page_title="Smart Flashcard Generator", page_icon="🧠")
st.title("🧠 Smart Flashcard Generator")

if "deck" not in st.session_state:
    st.session_state.deck = None
if "session" not in st.session_state:
    st.session_state.session = None

# --- Input ---
st.header("1. Add your material")
input_mode = st.radio("Input method", ["Paste text", "Upload file"])

raw_text = None
if input_mode == "Paste text":
    pasted = st.text_area("Paste your notes here", height=200)
    if pasted:
        raw_text = load_text(pasted, is_path=False)
else:
    uploaded = st.file_uploader("Upload a file", type=["txt", "md", "pdf", "docx"])
    if uploaded:
        temp_path = f"data/source_material/{uploaded.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        raw_text = load_text(temp_path, is_path=True)

# --- Settings ---
st.header("2. Configure")
col1, col2 = st.columns(2)
with col1:
    card_type = st.selectbox("Card type", ["flashcard", "mcq"])
    question_count = st.slider("Questions per chunk", 1, 10, config.questions_per_chunk)
with col2:
    topic = st.text_input("Topic / deck name", value="My Deck")
    difficulty_mix = st.text_input("Difficulty mix", value=config.difficulty_mix)

# --- Generate ---
if st.button("Generate flashcards", disabled=raw_text is None):
    with st.spinner("Chunking material..."):
        chunks = chunk_text(raw_text, strategy="auto", chunk_size=config.chunk_size)

    all_cards = []
    progress = st.progress(0.0)
    for i, chunk in enumerate(chunks):
        with st.spinner(f"Generating cards for section {i + 1}/{len(chunks)}..."):
            concepts = extract_concepts_for_chunks([chunk])
            if not concepts:
                continue
            if card_type == "flashcard":
                cards = generate_flashcards(concepts, question_count, difficulty_mix, topic)
            else:
                cards = generate_mcqs(concepts, question_count, difficulty_mix, topic)
            for c in cards:
                c.source_chunk_id = chunk.id
            all_cards.extend(cards)
        progress.progress((i + 1) / len(chunks))

    validated = validate_cards(all_cards)
    deck = Deck(name=topic)
    deck.add_cards(validated)
    st.session_state.deck = deck
    st.success(f"Generated {len(validated)} cards ({len(all_cards) - len(validated)} filtered as duplicate/malformed).")

# --- Review / Study ---
deck = st.session_state.deck
if deck and deck.cards:
    st.header("3. Study")
    mode = st.radio("Mode", ["Flashcards", "Quiz"])

    if st.button("Start session"):
        if mode == "Flashcards":
            st.session_state.session = FlashcardSession(list(deck.cards))
        else:
            st.session_state.session = QuizSession(list(deck.cards))

    session = st.session_state.session
    if session and not session.is_complete():
        card = session.current_card
        if isinstance(session, FlashcardSession):
            st.subheader(card.prompt)
            if st.toggle("Show answer"):
                st.write(card.answer)
            c1, c2 = st.columns(2)
            if c1.button("❌ Didn't know it"):
                session.mark(False)
                st.rerun()
            if c2.button("✅ Knew it"):
                session.mark(True)
                st.rerun()
        else:
            st.subheader(card.prompt)
            choice = st.radio("Choose an answer", session.current_options(), key=card.id)
            if st.button("Submit"):
                correct = session.submit_answer(choice)
                st.write("✅ Correct!" if correct else f"❌ Incorrect — answer: {card.answer}")
                st.rerun()
    elif session and session.is_complete():
        st.success("Session complete!")
        st.json(session.summary() if isinstance(session, FlashcardSession) else session.score())

    # --- Export ---
    st.header("4. Export")
    export_format = st.selectbox("Format", ["JSON", "CSV", "Anki (.apkg)"])
    if st.button("Export deck"):
        path_map = {
            "JSON": ("data/decks/export.json", export_json),
            "CSV": ("data/decks/export.csv", export_csv),
            "Anki (.apkg)": ("data/decks/export.apkg", export_anki),
        }
        out_path, export_fn = path_map[export_format]
        result_path = export_fn(deck, out_path)
        st.success(f"Exported to {result_path}")
        with open(result_path, "rb") as f:
            st.download_button("Download", f, file_name=result_path.name)