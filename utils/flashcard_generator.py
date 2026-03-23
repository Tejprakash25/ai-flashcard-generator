import json
import re
from typing import List, Dict

from utils.groq_client import call_groq

SYSTEM_PROMPT = """You are an expert educational content designer specializing in active-recall flashcards.

Your task is to read a text passage and generate high-quality flashcards that help learners deeply understand and retain the material.

RULES:
1. Focus on: definitions, key concepts, important facts, cause-effect relationships, and distinctions.
2. Questions must be specific, clear, and unambiguous — avoid vague or trivially simple questions.
3. Answers must be concise but complete — 1 to 3 sentences maximum.
4. Do NOT generate generic questions like "What is X?" unless X is a technical term that needs defining.
5. Prefer conceptual questions that test understanding, not just recall.
6. Generate between 3 and 8 flashcards per chunk depending on content density.
7. Return ONLY valid JSON — no markdown, no backticks, no extra text.

Output format (strict JSON array):
[
  {"question": "...", "answer": "..."},
  {"question": "...", "answer": "..."}
]"""


def _build_user_prompt(chunk: str) -> str:
    return f"""Read the following text and generate flashcards from it.

TEXT:
\"\"\"
{chunk}
\"\"\"

Return ONLY the JSON array of flashcards. No other text."""


def _parse_flashcards(raw: str) -> List[Dict[str, str]]:
   
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []  

    json_str = match.group(0)

    try:
        cards = json.loads(json_str)
    except json.JSONDecodeError:
        return []  
    valid_cards = []
    for card in cards:
        if (
            isinstance(card, dict)
            and "question" in card
            and "answer" in card
            and isinstance(card["question"], str)
            and isinstance(card["answer"], str)
            and card["question"].strip()
            and card["answer"].strip()
        ):
            valid_cards.append({
                "question": card["question"].strip(),
                "answer": card["answer"].strip(),
            })

    return valid_cards


def generate_flashcards_from_chunks(
    chunks: List[str],
    progress_callback=None,
) -> List[Dict[str, str]]:

    all_flashcards: List[Dict[str, str]] = []
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(i, total)

        prompt = _build_user_prompt(chunk)

        try:
            raw_response = call_groq(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.4,
                max_tokens=2048,
            )
            cards = _parse_flashcards(raw_response)
            all_flashcards.extend(cards)

        except Exception as e:
            print(f"[Warning] Chunk {i+1} failed: {e}")
            continue

    if progress_callback:
        progress_callback(total, total)

    return all_flashcards


def flashcards_to_csv(flashcards: List[Dict[str, str]]) -> str:
    import csv
    import io

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["question", "answer"])
    writer.writeheader()
    writer.writerows(flashcards)
    return output.getvalue()


def flashcards_to_txt(flashcards: List[Dict[str, str]]) -> str:
    lines = []
    for i, card in enumerate(flashcards, 1):
        lines.append(f"Q{i}: {card['question']}")
        lines.append(f"A{i}: {card['answer']}")
        lines.append("") 
    return "\n".join(lines)
