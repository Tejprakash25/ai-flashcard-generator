# 🃏 AI Flashcard Generator

Convert any PDF into high-quality study flashcards using Groq's ultra-fast LLaMA 3 inference.

**Pipeline:** PDF → Text → Chunks → Groq API → Flashcards → Streamlit UI

---

## ✨ Features

- Upload any text-based PDF
- Auto-generates Q&A flashcards focused on definitions, key concepts, and important facts
- Clean, dark-themed UI
- Download as **CSV** (Anki-compatible) or **plain text**
- Processes large PDFs chunk-by-chunk (no memory issues)

---

## 🚀 Quick Start (Local)

### 1. Clone the repo

```bash
git clone https://github.com/yourname/ai-flashcard-generator.git
cd ai-flashcard-generator
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Groq API key

Get a **free** API key at https://console.groq.com

```bash
cp .env.example .env
# Edit .env and paste your key:
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

### 5. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub (make sure `.env` is in `.gitignore` — it already is)
2. Go to https://share.streamlit.io → **New app**
3. Connect your GitHub repo, set **Main file path** to `app.py`
4. Under **Advanced settings → Secrets**, add:

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxx"
```

5. Click **Deploy** — your app goes live in ~60 seconds.

---

## 🗂 Project Structure

```
ai-flashcard-generator/
├── app.py                       # Streamlit UI + orchestration
├── requirements.txt
├── .env.example                 # Copy to .env and add your key
├── .gitignore
└── utils/
    ├── __init__.py
    ├── pdf_reader.py            # PyMuPDF text extraction + cleaning
    ├── chunker.py               # Split text into 700-word chunks
    ├── groq_client.py           # Groq REST API wrapper
    └── flashcard_generator.py  # Prompt engineering + JSON parsing
```

---

## 🔑 Tech Stack

| Tool | Purpose |
|------|---------|
| **Streamlit** | UI framework |
| **PyMuPDF (fitz)** | Fast PDF text extraction |
| **Groq API** | LLM inference (LLaMA 3.3 70B) |
| **python-dotenv** | Local env variable loading |

---

## ⚙️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Max chunks | 8 | Slide to process more/fewer pages |
| Chunk size | 700 words | Set in `chunker.py` |
| Model | `llama-3.3-70b-versatile` | Set in `groq_client.py` |
| Temperature | 0.4 | Controls creativity of flashcards |

---

## 📝 Flashcard Schema

```json
[
  {
    "question": "What is the difference between supervised and unsupervised learning?",
    "answer": "Supervised learning uses labeled data to train models, while unsupervised learning finds patterns in unlabeled data without explicit guidance."
  }
]
```

---

## ❓ FAQ

**Q: My PDF shows no text extracted.**  
A: The PDF is likely scanned (image-based). Only text-layer PDFs are supported.

**Q: I get an API error.**  
A: Check your `GROQ_API_KEY` is valid. Free tier has rate limits — wait a moment and retry.

**Q: How many flashcards will I get?**  
A: Typically 3–8 per chunk, so 24–64 for the default 8-chunk limit.
