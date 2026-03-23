import fitz  
import re


def extract_text_from_pdf(file_bytes: bytes) -> str:

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Could not open PDF: {e}")

    pages_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text") 
        if text.strip():
            pages_text.append(text)

    doc.close()

    if not pages_text:
        raise ValueError(
            "No extractable text found in this PDF. "
            "It may be scanned or image-based."
        )

    
    full_text = "\n".join(pages_text)
    return _clean_text(full_text)


def _clean_text(text: str) -> str:
    
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')

    lines = text.splitlines()
    cleaned_lines = [ln for ln in lines if not re.fullmatch(r"\s*\d+\s*", ln)]

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()
