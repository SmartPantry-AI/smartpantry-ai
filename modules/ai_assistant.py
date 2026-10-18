import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing. Check your .env file.")

client = OpenAI(api_key=api_key)

def ask_ai(question):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=question
    )

    return response.output_text
