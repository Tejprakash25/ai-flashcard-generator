"""
app.py
AI Flashcard Generator — Streamlit UI
Pipeline: PDF → Text → Chunks → Groq API → Flashcards
"""

import os
import streamlit as st
from dotenv import load_dotenv

from utils.pdf_reader import extract_text_from_pdf
from utils.chunker import chunk_text
from utils.flashcard_generator import (
    generate_flashcards_from_chunks,
    flashcards_to_csv,
    flashcards_to_txt,
)


load_dotenv() 

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
}

/* ── Main container width ── */
.block-container {
    max-width: 780px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
}

/* ── Hero title ── */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    color: #f0e6ff;
    text-align: center;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #8b8fa8;
    text-align: center;
    margin-bottom: 2.5rem;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* ── Accent pill ── */
.accent-pill {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #a855f7);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.75rem;
    border-radius: 100px;
    margin-bottom: 0.75rem;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(168, 85, 247, 0.35) !important;
    border-radius: 16px !important;
    background: rgba(124, 58, 237, 0.07) !important;
    padding: 1.5rem !important;
    transition: border-color 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(168, 85, 247, 0.65) !important;
}

/* ── Primary button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    cursor: pointer;
    transition: opacity 0.2s ease, transform 0.15s ease;
    margin-top: 0.5rem;
}
.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(0);
}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #d4b8ff !important;
    border-radius: 10px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    transition: background 0.2s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,255,255,0.12) !important;
}

/* ── Stat bar ── */
.stat-bar {
    display: flex;
    gap: 1.5rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}
.stat-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.75rem 1.25rem;
    flex: 1;
    text-align: center;
    min-width: 100px;
}
.stat-number {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: #c084fc;
    display: block;
}
.stat-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Flashcard ── */
.flashcard {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.25s ease, background 0.25s ease;
    position: relative;
    overflow: hidden;
}
.flashcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    background: linear-gradient(180deg, #7c3aed, #a855f7);
    border-radius: 3px 0 0 3px;
}
.flashcard:hover {
    border-color: rgba(168, 85, 247, 0.35);
    background: rgba(255,255,255,0.07);
}
.card-number {
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
    font-weight: 600;
}
.card-question {
    font-size: 1rem;
    color: #e8deff;
    font-weight: 600;
    line-height: 1.5;
    margin-bottom: 0.1rem;
}
.card-answer {
    font-size: 0.9rem;
    color: #9ca3af;
    line-height: 1.6;
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px solid rgba(255,255,255,0.07);
}

/* ── Divider ── */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.3), transparent);
    margin: 2rem 0;
}

/* ── Error / warning boxes ── */
.stAlert {
    border-radius: 12px !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #a855f7) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}

/* ── Text colors ── */
p, label, .stMarkdown { color: #c9d1d9; }
h1, h2, h3 { color: #f0e6ff; }
</style>
""", unsafe_allow_html=True)



def render_flashcard(card: dict, index: int):
    st.markdown(f"""
    <div class="flashcard">
        <div class="card-number">Card {index}</div>
        <div class="card-question">❓ {card['question']}</div>
        <div class="card-answer">💡 {card['answer']}</div>
    </div>
    """, unsafe_allow_html=True)



st.markdown('<div class="accent-pill">✦ Powered by Groq + Llama 3</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">AI Flashcard Generator</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Upload a PDF — get study-ready flashcards in seconds.</p>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Drop your PDF here or click to browse",
    type=["pdf"],
    help="Supports text-based PDFs. Scanned/image PDFs are not supported.",
)

if uploaded_file:
    col1, col2 = st.columns([2, 1])
    with col1:
        max_chunks = st.slider(
            "Max chunks to process",
            min_value=1,
            max_value=20,
            value=8,
            help="Each chunk ≈ 700 words. More chunks = more flashcards but longer wait.",
        )
    with col2:
        export_format = st.selectbox("Export format", ["CSV", "Plain text (.txt)"])

if uploaded_file:
    st.markdown("")  
    generate_clicked = st.button("🪄 Generate Flashcards", use_container_width=True)

    if generate_clicked:
        try:
            api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            st.error(
                "**GROQ_API_KEY not found.** "
                "Add it to your `.env` file locally, or to Streamlit Cloud secrets."
            )
            st.stop()

        # Set the key in env for the groq_client module
        os.environ["GROQ_API_KEY"] = api_key

        try:
            # 1. Extract text
            with st.spinner("📄 Reading PDF..."):
                file_bytes = uploaded_file.read()
                full_text = extract_text_from_pdf(file_bytes)

            word_count = len(full_text.split())
            st.success(f"✅ Extracted **{word_count:,} words** from your PDF.")

            # 2. Chunk text
            with st.spinner(" Splitting into chunks..."):
                chunks = chunk_text(full_text, max_words=700)
                chunks = chunks[:max_chunks]  # Respect user limit

            if not chunks:
                st.error("Could not extract meaningful text chunks. Please try a different PDF.")
                st.stop()

            # 3. Generate flashcards with progress bar
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("**⚙️ Generating flashcards...**")
            progress_bar = st.progress(0)
            status_text = st.empty()

            all_flashcards = []

            from utils.flashcard_generator import generate_flashcards_from_chunks

            def update_progress(current, total):
                pct = int((current / total) * 100) if total > 0 else 0
                progress_bar.progress(pct)
                if current < total:
                    status_text.markdown(
                        f"<small style='color:#8b8fa8'>Processing chunk {current + 1} of {total}...</small>",
                        unsafe_allow_html=True,
                    )
                else:
                    status_text.markdown(
                        "<small style='color:#a855f7'>✓ Done!</small>",
                        unsafe_allow_html=True,
                    )

            all_flashcards = generate_flashcards_from_chunks(
                chunks, progress_callback=update_progress
            )

            # Store in session state so results persist
            st.session_state["flashcards"] = all_flashcards
            st.session_state["filename"] = uploaded_file.name

        except ValueError as e:
            st.error(f"PDF Error: {e}")
            st.stop()
        except RuntimeError as e:
            st.error(f"API Error: {e}")
            st.stop()


if "flashcards" in st.session_state and st.session_state["flashcards"]:
    flashcards = st.session_state["flashcards"]
    filename = st.session_state.get("filename", "document")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Stat bar
    chunk_count = len(chunk_text(
        "", max_words=700  # dummy call just for display — use stored count if available
    ))
    st.markdown(f"""
    <div class="stat-bar">
        <div class="stat-item">
            <span class="stat-number">{len(flashcards)}</span>
            <span class="stat-label">Flashcards</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">{len(flashcards) * 2}</span>
            <span class="stat-label">Study Items</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">~{max(1, len(flashcards) // 5)}m</span>
            <span class="stat-label">Est. Review</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Download buttons
    st.markdown("**📥 Download your flashcards**")
    col_dl1, col_dl2 = st.columns(2)

    from utils.flashcard_generator import flashcards_to_csv, flashcards_to_txt
    import re

    base_name = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)

    with col_dl1:
        csv_data = flashcards_to_csv(flashcards)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name=f"{base_name}_flashcards.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_dl2:
        txt_data = flashcards_to_txt(flashcards)
        st.download_button(
            "⬇️ Download TXT",
            data=txt_data,
            file_name=f"{base_name}_flashcards.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Flashcard display
    st.markdown(f"### 🃏 Your {len(flashcards)} Flashcards")
    st.markdown(
        "<small style='color:#6b7280'>All questions and answers are shown below. "
        "Use CSV for Anki import.</small>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    for i, card in enumerate(flashcards, 1):
        render_flashcard(card, i)

elif "flashcards" in st.session_state and not st.session_state["flashcards"]:
    st.warning(
        "No flashcards were generated. The PDF may not contain enough structured content. "
        "Try a different file."
    )

st.markdown("""
<div style='text-align:center; margin-top:4rem; color:#374151; font-size:0.8rem;'>
    Built with Streamlit · Groq · PyMuPDF &nbsp;·&nbsp; 
    <a href="https://groq.com" style='color:#6b7280; text-decoration:none;'>Get a free Groq API key →</a>
</div>
""", unsafe_allow_html=True)
