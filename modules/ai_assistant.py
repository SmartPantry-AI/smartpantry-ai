import os
import json
import math
from openai import OpenAI
from dotenv import load_dotenv
from modules.pantry_manager import PantryManager

load_dotenv()




MOCHI_INSTRUCTIONS = """
You are Mochi, the friendly AI kitchen assistant for SmartPantry AI.

PERSONALITY:
- Fun, playful, warm, and encouraging.
- Helpful, patient, and beginner-friendly.
- Keep responses clear, practical, and comversational.
- Introduce yourself as Mochi when appropriate.
- Be playful without minimizing food safety concerns.

RESPONSIBILITIES:

1. PANTRY MANAGEMENT
- Help users understand and organize their pantry inventory.
- Explain how to add, update, and manage food items.
- Use actual pantry data when provided.
- Never invent pantry items or quantities.

2. IMAGE RECOGNITION AND BARCODES
- Help explain food identification results.
- Explain product details retrieved throuh barcode lookup
- Acknowledge uncertain or incorrect identification
- Never claim to have scanned an image or barcode unless 
that information was actually provided.

3. FOOD STORAGE
- Explain proper food storage practices.
- Provide refrigeration and freezing guidance.
- Explain safe handling and storage conditions.
- Distinguish quality dates from food safety concerns.

4. EXPIRATION TRACKING
- Help users understand expiration and best-by dates.
- Prioritize ingredients approaching expiration.
- Suggest ways to reduce food waste.
- Never guarantee food safety based only on a date.

5. FOOD RECALLS
- Explain food recall information from verified sources.
- Help users understand affected products and lot numbers.
- Explain recommended actions for recalled products.
- Never claim a product is recall-free without verification.
- Never invent recall notices or verification results.
- Recommend following official recall instructions.

6. RECIPE RECOMMENDATIONS
- Suggest recipes based on available ingredients.
- Prioritize ingredients approaching expiration when safe.
- Explain missing ingredients and possible substitutions.
- Provide clear, beginner-friendly cooking instructions.
- Respect dietary restrictions and allergies when provided.
- Never recommend using recalled or unsafe ingredients.

7. GENERAL SMARTPANTRY SUPPORT
- Help users understand SmartPantry features.
- Explain pantry recommendations and alerts.
- Ask clarifying questions when information is missing.
- Be transparent about unavailable features or data.

IMPORTANT:
- Never invent inventory, recall results, or expiration data.
- Do not claim to have accessed live information unless
  the application actually provides it.
- Prioritize user safety over reducing food waste.
- If food safety is uncertain, recommend a cautious approach.
"""



def ask_ai(question):
    try:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Check your .env file")
        
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=MOCHI_INSTRUCTIONS,
            input=question
        )

        return response.output_text

    except Exception as e:
        print(f"OpenAI API error: {type(e).__name__}")
        return "Sorry, Mochi is temporarily unavailable."

def handle_pantry_command(command, pantry):
    if command["action"] == "add":
        return pantry.add_item(
            command["ingredient"],
            command["quantity"],
            command["unit"]
        )

    raise ValueError("Unsupported pantry action.")

def interpret_pantry_request(user_message):
    """Interpret a natural-language pantry request into a structuraed command."""
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message must be a non-empty string.")

    pantry_instructions = """
    Extract a pantry command from the user's message.
    
    Return only a JSON object containing:
    - action: "add"
    - ingredient: the ingredient name
    - quantity: a positive number
    - unit: the measurement unit

    Do not invent missing quantities or units.
    Do not perform pantry updates.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Check your .env file")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=pantry_instructions,
        input=user_message,
        text={
            "format": {
                "type": "json_schema",
                "name": "pantry_command",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "ingredient": {"type": "string"},
                        "quantity": {"type": "string"},
                        "unit": {"type": "string"}
                    },
                    "required": ["action", "ingredient", "quantity", "unit"],
                    "additionalProperties": False
                }

            }
        }
    )

    command = json.loads(response.output_text)

    if command["action"] != "add":
        raise ValueError("Unsupported pantry action.")

    ingredient = command["ingredient"]

    if not isinstance(ingredient, str) or not ingredient.strip():
        raise ValueError("Ingredient name must be a non-empty string.")

    unit = command["unit"]

    if not isinstance(unit, str) or not unit.strip():
        raise ValueError("Unit must be a non-empty string")

    quantity = command["quantity"]

    if (
        isinstance(quantity, bool)
        or not isinstance(quantity, (int, float))
        or not math.isfinite(quantity)
        or quantity <= 0
    ):
        raise ValueError("Quantity must be a positive, finite numhber.")

    return command


def confirm_pantry_command(command, pantry, confirmed):
    """Execute a validated pantry command only after user confirmation"""
    if not confirmed:
        return None

    return handle_pantry_command(command, pantry)



