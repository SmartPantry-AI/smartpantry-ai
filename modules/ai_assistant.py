import os
import json
import math
from datetime import date
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
- Never claim that you have added, updated, or deleted a pantry
  item unless the SmartPantry application has confirmed the action.
- Do not say "Adding now", "Done", or "I've added it" when
  responding through normal conversation.
- If a user requests a pantry change that has not been executed,
  explain that the change has not been saved.
- Pantry changes require user confirmation before execution.

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



def ask_ai(question, conversation_history=None):
    try:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Check your .env file")
        
        client = OpenAI(api_key=api_key)

        messages = conversation_history if conversation_history is not None else [
            {"role": "user", "content": question}
        ]

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=MOCHI_INSTRUCTIONS,
            input=messages,
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
                        "quantity": {"type": "number"},
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


def handle_supabase_pantry_command(command, client, *, storage_metadata=None):
    """Add a confirmed pantry item to the authenticated user's Supabase pantry."""

    if not isinstance(command, dict):
        raise ValueError("Pantry command must be a dictionary.")

    ingredient = command.get("ingredient")
    quantity = command.get("quantity")
    unit = command.get("unit")

    if not isinstance(ingredient, str) or not ingredient.strip():
        raise ValueError("Ingredient name is required.")

    if (
        isinstance(quantity, bool)
        or not isinstance(quantity, (int, float))
        or not math.isfinite(quantity)
        or quantity <= 0
    ):
        raise ValueError("Quantity must be a positive, finite number.")

    if not isinstance(unit, str) or not unit.strip():
        raise ValueError("Unit is required.")

    if command["action"] != "add":
        raise ValueError("Unsupported pantry action.")

    from modules.supabase_pantry import add_pantry_item

    allowed_storage_fields = (
        "purchase_date",
        "expiration_date",
        "storage_location",
        "prepared_date",
        "food_classification",
        "preparation_state",
        "package_state",
        "opened_date",
        "thawed_date",
    )

    if storage_metadata is not None and not isinstance(storage_metadata, dict):
        raise ValueError("Storage metadata must be a dictionary.")

    metadata = storage_metadata or {}

    allowed_values = {
        "storage_location": {"REFRIGERATOR", "FREEZER", "PANTRY"},
        "food_classification": {"REGULAR", "COOKED"},
        "preparation_state": {"WHOLE", "CUT", "RAW", "COOKED"},
        "package_state": {"OPENED", "UNOPENED"},
    }

    for field, valid_values in allowed_values.items():
        value = metadata.get(field)

        if value is not None:
            if not isinstance(value, str) or value not in valid_values:
                raise ValueError(f"Invalid {field}.")

    food_classification = metadata.get("food_classification")
    preparation_state = metadata.get("preparation_state")

    if (
        food_classification == "COOKED"
        and preparation_state in {"WHOLE", "CUT", "RAW"}
    ):
        raise ValueError(
            "For cooked food, select Cooked as the preparation "
            "state or leave it unspecified."
        )

    if (
        food_classification == "REGULAR"
        and preparation_state == "COOKED"
    ):
        raise ValueError(
            "Please select Cooked food / leftovers "
            "as the food classification."
        )

    date_fields = (
        "purchase_date",
        "expiration_date",
        "prepared_date",
        "opened_date",
        "thawed_date",
    )

    parsed_dates = {}

    for field in date_fields:
        value = metadata.get(field)

        if value is None:
            continue

        if not isinstance(value, str):
            raise ValueError(f"Invalid {field}. Expected YYYY-MM-DD.")

        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            raise ValueError(
                f"Invalid {field}. Expected YYYY-MM-DD."
            ) from None

        if parsed_date.isoformat() != value:
            raise ValueError(f"Invalid {field}. Expected YYYY-MM-DD.")

        parsed_dates[field] = parsed_date

    today = date.today()

    for field in (
        "purchase_date",
        "prepared_date",
        "opened_date",
        "thawed_date",
    ):
        if field in parsed_dates and parsed_dates[field] > today:
            label = field.replace("_", " ").capitalize()
            raise ValueError(f"{label} cannot be in the future.")

    purchase_date = parsed_dates.get("purchase_date")
    opened_date = parsed_dates.get("opened_date")
    thawed_date = parsed_dates.get("thawed_date")

    if purchase_date and opened_date and opened_date < purchase_date:
        raise ValueError(
            "Opening date cannot precede the purchase date."
        )

    if purchase_date and thawed_date and thawed_date < purchase_date:
        raise ValueError(
            "Thawing date cannot precede the purchase date."
        )

    storage_fields = {
        field: metadata[field]
        for field in allowed_storage_fields
        if field in metadata
    }

    return add_pantry_item(
        client=client,
        name=command["ingredient"],
        quantity=command["quantity"],
        unit=command["unit"],
        **storage_fields,
    )


def format_pantry_inventory(pantry_items):
    """Format saved pantry records for Mochi's response."""

    if not pantry_items:
        return "Your pantry is currently empty."

    item_list = [
        f"- {item['name']}: {item['quantity']} {item['unit']}"
        for item in pantry_items
    ]

    return (
        "Here's what's currently in your pantry:\n\n"
        + "\n".join(item_list)
    )