
"""AI-powered food image recognition for SmartPantry."""

import base64
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


def recognize_food(image_path):
    """Identify food in an image using a pretrained OpenAI model."""

    image_path = Path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Check your .env file.")

    image_base64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Identify the main food item in this image. "
                            "Return only its common food name. "
                            "If the image does not clearly contain food, "
                            "return 'Unknown'. Do not guess."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
    )

    return response.output_text.strip()
