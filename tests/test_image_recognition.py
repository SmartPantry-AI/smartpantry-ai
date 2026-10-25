import pytest
from unittest.mock import patch, MagicMock

from modules.image_recognition import recognize_food

def test_recognize_food_missing_image():
    with pytest.raises(FileNotFoundError):
        recognize_food("missing_food.jpg")

def test_recognize_food_mock_response(tmp_path):
    image_file = tmp_path / "apple.jpg"
    image_file.write_bytes(b"fake image data")
    with patch("modules.image_recognition.os.getenv", return_value="fake-test-key"), \
         patch("modules.image_recognition.OpenAI") as mock_openai:    
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_client.responses.create.return_value.output_text = "Apple"
        result = recognize_food(image_file)

        assert result == "Apple"
        

