import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from modules.ai_assistant import ask_ai, MOCHI_INSTRUCTIONS, handle_pantry_command, interpret_pantry_request, confirm_pantry_command, format_pantry_inventory

def test_ask_ai_returns_response():
    #Create a fake OpenAI response
    mock_response = MagicMock()
    mock_response.output_text = "You can make spinach pasta."

    #Replace the real API call with a mock
    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_create = mock_openai.return_value.responses.create
        mock_create.return_value = mock_response

        result = ask_ai("What can I cook with spinach?")

    #Check the returned answer
    assert result == "You can make spinach pasta."

    #Verify that the function called OpenAI correctly
    mock_create.assert_called_once_with(
        model="gpt-4.1-mini",
        instructions=MOCHI_INSTRUCTIONS,
        input=[
            {"role": "user", "content": "What can I cook with spinach?"}
        ]
    )

def test_ask_ai_handles_api_error():
    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_create = mock_openai.return_value.responses.create
        mock_create.side_effect = Exception("Simulated API failure")

        result = ask_ai("What can I cook with chicken?")

    assert result == "Sorry, Mochi is temporarily unavailable."
    
def test_mochi_identity_and_safety_instructions():
    instructions = MOCHI_INSTRUCTIONS.lower()

    assert "mochi" in instructions
    assert "food recalls" in instructions
    assert "food storage" in instructions
    assert "image recognition"  in instructions
    assert "never invent" in instructions
    
from modules.ai_assistant import handle_pantry_command
from modules.pantry_manager import PantryManager


def test_mochi_adds_ingredient_to_pantry():
    pantry = PantryManager()

    command = {
        "action": "add",
        "ingredient": "apples",
        "quantity": 3,
        "unit": "pieces"
    }

    result = handle_pantry_command(command, pantry)

    assert result == {
        "name": "apple",
        "quantity": 3,
        "unit": "pieces"
    }

    assert pantry.get_items() == [result]


def test_mochi_rejects_unsupported_action():
    pantry = PantryManager()

    command = {
        "action": "delete",
        "ingredient": "apple",
        "quantity": 3,
        "unit": "pieces"
    }

    with pytest.raises(ValueError, match="Unsupported pantry action"):
        handle_pantry_command(command, pantry)

    assert pantry.get_items() == []


def test_interpret_pantry_request_rejects_empty_message():
    with pytest.raises(ValueError, match="User message must be a non-empty string"):
        interpret_pantry_request("")


def test_interpret_pantry_request_returns_structured_command():
    mock_response = MagicMock()
    mock_response.output_text = (
        '{"action":"add","ingredient":"apples",'
        '"quantity":3,"unit":"pieces"}'
    )

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_create = mock_openai.return_value.responses.create
        mock_create.return_value = mock_response

        command = interpret_pantry_request("Mochi, I bought 3 apples.")

    assert command == {
        "action": "add",
        "ingredient": "apples",
        "quantity": 3,
        "unit": "pieces"
    }

def test_interpret_pantry_request_rejects_negative_quantity():
    mock_response = MagicMock()
    mock_response.output_text = (
        '{"action":"add","ingredient":"apples",'
        '"quantity":-3,"unit":"pieces"}'
    )

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_openai.return_value.responses.create.return_value = mock_response

        with pytest.raises(ValueError):
            interpret_pantry_request("I bought negative 3 apples.")


def test_interpret_pantry_request_rejects_unsupported_action():
    mock_response = MagicMock()
    mock_response.output_text = (
        '{"action":"delete","ingredient":"apples",'
        '"quantity":3,"unit":"pieces"}'
    )

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_openai.return_value.responses.create.return_value = mock_response

        with pytest.raises(ValueError, match="Unsupported pantry action"):
            interpret_pantry_request("Delete 3 apples.")


def test_interpret_pantry_request_rejects_empty_ingredient():
    mock_response = MagicMock()
    mock_response.output_text = (
        '{"action":"add","ingredient":"",'
        '"quantity":3,"unit":"pieces"}'
    )

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_openai.return_value.responses.create.return_value = mock_response

        with pytest.raises(ValueError, match="Ingredient name must be a non-empty string"):
            interpret_pantry_request("Add 3 items.")


def test_interpret_pantry_request_rejects_empty_unit():
    mock_response = MagicMock()
    mock_response.output_text = (
        '{"action":"add","ingredient":"milk",'
        '"quantity":2,"unit":""}'
    )

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_openai.return_value.responses.create.return_value = mock_response

        with pytest.raises(ValueError, match="Unit must be a non-empty string"):
            interpret_pantry_request("Add 2 milk.")


def test_mochi_does_not_update_pantry_without_confirmation():
    pantry = PantryManager()

    command = {
        "action": "add",
        "ingredient": "apples",
        "quantity": 3,
        "unit": "pieces"
    }

    result = confirm_pantry_command(command, pantry, confirmed=False)

    assert result is None
    assert pantry.get_items() == []


def test_mochi_updates_pantry_after_confirmation():
    pantry = PantryManager()

    command = {
        "action": "add",
        "ingredient": "apples",
        "quantity": 3,
        "unit": "pieces"
    }

    result = confirm_pantry_command(command, pantry, confirmed=True)

    assert result == {
        "name": "apple",
        "quantity": 3,
        "unit": "pieces"
    }

    assert pantry.get_items() == [result]


def test_mochi_complete_pantry_addition_workflow():
    pantry = PantryManager()

    mock_response = MagicMock()
    mock_response.output_text = (
        '{"action":"add","ingredient":"apples",'
        '"quantity":3,"unit":"pieces"}'
    )

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_openai.return_value.responses.create.return_value = mock_response

        command = interpret_pantry_request("Mochi, I bought 3 apples.")

    # Simulate the user approving the interpreted command
    result = confirm_pantry_command(command, pantry, confirmed=True)

    assert result == {
        "name": "apple",
        "quantity": 3,
        "unit": "pieces"
    }

    assert pantry.get_items() == [result]


def test_ask_ai_receives_conversation_history():
    history = [
        {"role": "user", "content": "How should I store spinach?"},
        {"role": "assistant", "content": "Keep it refrigerated."},
        {"role": "user", "content": "Can I freeze it?"}
    ]

    mock_response = MagicMock()
    mock_response.output_text = "Yes, you can freeze spinach."

    with patch("modules.ai_assistant.OpenAI") as mock_openai:
        mock_create = mock_openai.return_value.responses.create
        mock_create.return_value = mock_response

        result = ask_ai(
            "Can I freeze it?",
            conversation_history=history
        )

        assert result == "Yes, you can freeze spinach."

        mock_create.assert_called_once_with(
            model="gpt-4.1-mini",
            instructions=MOCHI_INSTRUCTIONS,
            input=history
        )    
        

def test_mochi_adds_item_to_supabase(monkeypatch):
    from modules.ai_assistant import handle_supabase_pantry_command

    saved_items = []

    def mock_add_pantry_item(client, name, quantity, unit):
        saved_items.append({
            "client": client,
            "name": name,
            "quantity": quantity,
            "unit": unit,
        })
        return [{"id": 101, "name": name}]

    monkeypatch.setattr(
        "modules.supabase_pantry.add_pantry_item",
        mock_add_pantry_item,
    )

    fake_client = object()

    command = {
        "action": "add",
        "ingredient": "rice",
        "quantity": 2,
        "unit": "cups",
    }

    result = handle_supabase_pantry_command(
        command,
        fake_client,
    )

    assert saved_items == [{
        "client": fake_client,
        "name": "rice",
        "quantity": 2,
        "unit": "cups",
    }]

    assert result == [{"id": 101, "name": "rice"}]



import pytest


@pytest.mark.parametrize("command", [
    {"action": "add", "ingredient": "", "quantity": 2, "unit": "cups"},
    {"action": "add", "ingredient": "rice", "quantity": -2, "unit": "cups"},
    {"action": "add", "ingredient": "rice", "quantity": 0, "unit": "cups"},
    {"action": "add", "ingredient": "rice", "quantity": 2, "unit": ""},
    {"action": "delete", "ingredient": "rice", "quantity": 2, "unit": "cups"},
    None,
])
def test_mochi_rejects_invalid_supabase_commands(command):
    from modules.ai_assistant import handle_supabase_pantry_command

    with pytest.raises(ValueError):
        handle_supabase_pantry_command(command, object())

def test_mochi_formats_pantry_inventory():
    pantry_items = [
        {"name": "Banana", "quantity": 5, "unit": "item"},
        {"name": "Rice", "quantity": 10, "unit": "lb"},
    ]

    result = format_pantry_inventory(pantry_items)

    assert "Banana: 5 item" in result
    assert "Rice: 10 lb" in result


def test_mochi_handles_empty_pantry():
    result = format_pantry_inventory([])

    assert result == "Your pantry is currently empty."


def test_mochi_preserves_separate_pantry_batches():
    pantry_items = [
        {"name": "Rice", "quantity": 10, "unit": "lb"},
        {"name": "Rice", "quantity": 2, "unit": "cups"},
    ]

    result = format_pantry_inventory(pantry_items)

    assert "Rice: 10 lb" in result
    assert "Rice: 2 cups" in result

def test_mochi_adds_item_with_storage_metadata():
    from modules.ai_assistant import handle_supabase_pantry_command

    fake_client = object()

    command = {
        "action": "add",
        "ingredient": "cheddar cheese",
        "quantity": 1,
        "unit": "item",
    }

    metadata = {
        "purchase_date": "2026-11-20",
        "expiration_date": "2026-12-20",
        "storage_location": "REFRIGERATOR",
        "prepared_date": None,
        "food_classification": "REGULAR",
        "preparation_state": None,
        "package_state": "OPENED",
        "opened_date": "2026-11-24",
        "thawed_date": None,
    }

    with patch("modules.supabase_pantry.add_pantry_item") as mock_add:
        mock_add.return_value = [
            {"id": 102, "name": "cheddar cheese"}
        ]

        result = handle_supabase_pantry_command(
            command,
            fake_client,
            storage_metadata=metadata,
        )

        mock_add.assert_called_once_with(
            client=fake_client,
            name="cheddar cheese",
            quantity=1,
            unit="item",
            **metadata,
        )

    assert result == [
        {"id": 102, "name": "cheddar cheese"}
    ]


@pytest.mark.parametrize("metadata", [
    "invalid metadata",
    [],
    {"storage_location": "GARAGE"},
    {"food_classification": "FRESH"},
    {"preparation_state": "FROZEN"},
    {"package_state": "SEALED"},
    {"storage_location": 123},
    {"food_classification": ""},
    {"preparation_state": ["RAW"]},
])
def test_mochi_rejects_invalid_storage_metadata(metadata):
    from modules.ai_assistant import handle_supabase_pantry_command

    command = {
        "action": "add",
        "ingredient": "apple",
        "quantity": 2,
        "unit": "item",
    }

    with patch("modules.supabase_pantry.add_pantry_item") as mock_add:
        with pytest.raises(ValueError):
            handle_supabase_pantry_command(
                command,
                object(),
                storage_metadata=metadata,
            )

        mock_add.assert_not_called()


@pytest.mark.parametrize("classification, preparation", [
    ("COOKED", "RAW"),
    ("COOKED", "WHOLE"),
    ("COOKED", "CUT"),
    ("REGULAR", "COOKED"),
])
def test_mochi_rejects_contradictory_food_classification(
    classification, preparation
):
    from modules.ai_assistant import handle_supabase_pantry_command

    command = {
        "action": "add",
        "ingredient": "chicken",
        "quantity": 1,
        "unit": "item",
    }

    metadata = {
        "food_classification": classification,
        "preparation_state": preparation,
    }

    with patch("modules.supabase_pantry.add_pantry_item") as mock_add:
        with pytest.raises(ValueError):
            handle_supabase_pantry_command(
                command,
                object(),
                storage_metadata=metadata,
            )

        mock_add.assert_not_called()


@pytest.mark.parametrize("metadata", [
    {"purchase_date": "11/25/2026"},
    {"expiration_date": "2026-02-30"},
    {"prepared_date": "2026-13-01"},
    {"opened_date": "20261125"},
    {"thawed_date": ""},
    {"purchase_date": 20261125},
    {"prepared_date": "yesterday"},
    {"opened_date": "2026-11-25T12:00:00"},
    {"thawed_date": "2026-02-29"},
])
def test_mochi_rejects_invalid_storage_dates(metadata):
    from modules.ai_assistant import handle_supabase_pantry_command

    command = {
        "action": "add",
        "ingredient": "chicken",
        "quantity": 1,
        "unit": "item",
    }

    with patch("modules.supabase_pantry.add_pantry_item") as mock_add:
        with pytest.raises(ValueError):
            handle_supabase_pantry_command(
                command,
                object(),
                storage_metadata=metadata,
            )

        mock_add.assert_not_called()


@pytest.mark.parametrize("metadata", [
    {"purchase_date": (date.today() + timedelta(days=1)).isoformat()},
    {"prepared_date": (date.today() + timedelta(days=1)).isoformat()},
    {"opened_date": (date.today() + timedelta(days=1)).isoformat()},
    {"thawed_date": (date.today() + timedelta(days=1)).isoformat()},
    {
        "purchase_date": "2026-11-24",
        "opened_date": "2026-11-20",
    },
    {
        "purchase_date": "2026-11-24",
        "thawed_date": "2026-11-20",
    },
])
def test_mochi_rejects_invalid_date_chronology(metadata):
    from modules.ai_assistant import handle_supabase_pantry_command

    command = {
        "action": "add",
        "ingredient": "chicken",
        "quantity": 1,
        "unit": "item",
    }

    with patch("modules.supabase_pantry.add_pantry_item") as mock_add:
        with pytest.raises(ValueError):
            handle_supabase_pantry_command(
                command,
                object(),
                storage_metadata=metadata,
            )

        mock_add.assert_not_called()

@pytest.mark.parametrize("metadata", [
    {},
    {"food_classification": "COOKED"},
    {"food_classification": "COOKED", "preparation_state": "COOKED"},
    {"food_classification": "REGULAR", "preparation_state": "WHOLE"},
    {"expiration_date": (date.today() + timedelta(days=30)).isoformat()},
    {"expiration_date": (date.today() - timedelta(days=5)).isoformat()},
    {
        "purchase_date": "2026-11-24",
        "opened_date": "2026-11-24",
        "package_state": "OPENED",
    },
    {
        "purchase_date": None,
        "storage_location": None,
        "food_classification": None,
        "preparation_state": None,
        "package_state": None,
        "expiration_date": None,
        "prepared_date": None,
        "opened_date": None,
        "thawed_date": None,
    },
])
def test_mochi_accepts_valid_storage_metadata(metadata):
    from modules.ai_assistant import handle_supabase_pantry_command

    fake_client = object()

    command = {
        "action": "add",
        "ingredient": "chicken",
        "quantity": 1,
        "unit": "item",
    }

    with patch("modules.supabase_pantry.add_pantry_item") as mock_add:
        mock_add.return_value = [{"id": 103, "name": "chicken"}]

        result = handle_supabase_pantry_command(
            command,
            fake_client,
            storage_metadata=metadata,
        )

        mock_add.assert_called_once_with(
            client=fake_client,
            name="chicken",
            quantity=1,
            unit="item",
            **metadata,
        )

    assert result == [{"id": 103, "name": "chicken"}]


    