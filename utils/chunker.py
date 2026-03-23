from typing import List


def chunk_text(text: str, max_words: int = 700) -> List[str]:

    if not text.strip():
        return []

   
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: List[str] = []
    current_chunk: List[str] = []
    current_word_count = 0

    for para in paragraphs:
        para_words = len(para.split())

        
        if para_words > max_words:
            sentences = _split_into_sentences(para)
            for sentence in sentences:
                sent_words = len(sentence.split())
                if current_word_count + sent_words > max_words and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_word_count = sent_words
                else:
                    current_chunk.append(sentence)
                    current_word_count += sent_words
        else:
            if current_word_count + para_words > max_words and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_word_count = para_words
            else:
                current_chunk.append(para)
                current_word_count += para_words

  
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    chunks = [c for c in chunks if len(c.split()) >= 30]

    return chunks


def _split_into_sentences(text: str) -> List[str]:
    import re
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [s.strip() for s in sentences if s.strip()]
