import os
import json
import requests
from typing import Optional

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def call_groq(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.4,
    max_tokens: int = 2048,
) -> str:
 
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file or Streamlit secrets."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("Groq API request timed out. Please try again.")
    except requests.exceptions.HTTPError as e:
       
        try:
            err_msg = response.json().get("error", {}).get("message", str(e))
        except Exception:
            err_msg = str(e)
        raise RuntimeError(f"Groq API error: {err_msg}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error calling Groq API: {e}")

    data = response.json()
    return data["choices"][0]["message"]["content"]
