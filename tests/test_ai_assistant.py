from unittest.mock import MagicMock, patch
from modules.ai_assistant import ask_ai, MOCHI_INSTRUCTIONS

def test_ask_ai_returns_response():
    #Create a fake OpenAI response
    mock_response = MagicMock()
    mock_response.output_text = "You can make spinach pasta."

    #Replace the real API call with a mock
    with patch("modules.ai_assistant.client.responses.create") as mock_create:
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
    with patch("modules.ai_assistant.client.responses.create") as mock_create:
        mock_create.side_effect = Exception("API connection failed")

        result = ask_ai("What can I cook with chicken?")

    assert result == "Sorry, Mochi is temporarily unavailable."
    
def test_mochi_identity_and_safety_instructions():
    instructions = MOCHI_INSTRUCTIONS.lower()

    assert "mochi" in instructions
    assert "food recalls" in instructions
    assert "food storage" in instructions
    assert "image recognition"  in instructions
    assert "never invent" in instructions
    
        