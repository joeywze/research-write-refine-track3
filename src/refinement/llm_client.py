#function: model API connection

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is missing. Add it to your .env file."
    )

client = OpenAI(api_key=api_key)


def generate_text(prompt: str) -> str:
    """Send a prompt to the model and return its response."""

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return response.output_text.strip()
