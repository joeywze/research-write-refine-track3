import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
_client = None


def generate_text(prompt: str) -> str:
    """Send a prompt to the model and return its response."""
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")
        _client = OpenAI(api_key=api_key)

    response = _client.responses.create(model=MODEL, input=prompt)
    text = response.output_text.strip()

    if not text:
        raise RuntimeError("The model returned no text.")

    return text
