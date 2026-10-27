import pytest
from unittest.mock import MagicMock, patch
from modules.ai_assistant import ask_ai, MOCHI_INSTRUCTIONS, handle_pantry_command, interpret_pantry_request, confirm_pantry_command

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
        input="What can I cook with spinach?"
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

    
        
