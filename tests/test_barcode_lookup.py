import pytest
import requests
from unittest.mock import patch, MagicMock

from modules.barcode_lookup import decode_barcode, identify_product


def test_decode_barcode_image_not_loaded():
    with patch("modules.barcode_lookup.cv2.imread", return_value=None):
        result, error = decode_barcode("missing_image.jpg")

    assert result is None
    assert error == "Image could not be loaded."

def test_decode_barcode_no_barcode_detected():
    mock_image = MagicMock()
    mock_detector = MagicMock()

    mock_detector.detectAndDecodeWithType.return_value = (
        False, (), (), None
    )

    with patch(
        "modules.barcode_lookup.cv2.imread",
        return_value=mock_image
    ), patch(
        "modules.barcode_lookup.cv2.barcode.BarcodeDetector",
        return_value=mock_detector
    ):
        result, error = decode_barcode("no_barcode.jpg")

    assert result is None
    assert error == "No barcode detected."


def test_decode_barcode_success():
    mock_image = MagicMock()
    mock_detector = MagicMock()

    mock_detector.detectAndDecodeWithType.return_value = (
        True, ("041220053667",), ("UPC_A",), None
    )

    with patch(
        "modules.barcode_lookup.cv2.imread",
        return_value=mock_image
    ), patch(
        "modules.barcode_lookup.cv2.barcode.BarcodeDetector",
        return_value=mock_detector
    ):
        result, error = decode_barcode("bread.jpg")

    assert result == {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }
    assert error is None

def test_identify_product_success():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()

    mock_response.json.return_value = {
        "product": {
            "product_name": "Honey Wheat",
            "brands": "Hill Country Fare",
            "categories": "Bread",
            "quantity": "20 oz"
        }
    }

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ) as mock_get:
        result, error = identify_product("bread.jpg")

    assert error is None

    assert result == {
        "barcode": "041220053667",
        "barcode_type": "UPC_A",
        "product_name": "Honey Wheat",
        "brand": "Hill Country Fare",
        "source_category": "Bread",
        "quantity": "20 oz",
        "product_data_source": "Open Food Facts",
        "input_method": "barcode_image",
        "user_confirmed": False
    }

    mock_get.assert_called_once_with(
        "https://world.openfoodfacts.org/api/v3/product/041220053667.json",
        headers={
            "User-Agent": "SmartPantryAI/1.0 (student capstone project)"
        },
        timeout=10
    )

    mock_response.raise_for_status.assert_called_once()


def test_identify_product_barcode_failure():
    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(None, "No barcode detected.")
    ), patch(
        "modules.barcode_lookup.requests.get"
    ) as mock_get:
        result, error = identify_product("no_barcode.jpg")

    assert result is None
    assert error == "No barcode detected."

    mock_get.assert_not_called()


def test_identify_product_not_found():
    mock_barcode = {
        "barcode": "000000000000",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {"status": 0}

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ):
        result, error = identify_product("unknown_product.jpg")

    assert result is None
    assert error == "Product not found. Manual entry required."

def test_identify_product_http_error():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError("503 Service Unavailable")
    )

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ):
        result, error = identify_product("bread.jpg")

    assert result is None
    assert error == (
        "Open Food Facts request failed: 503 Service Unavailable"
    )

    mock_response.json.assert_not_called()


def test_identify_product_timeout():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        side_effect=requests.Timeout("Request timed out")
    ):
        result, error = identify_product("bread.jpg")

    assert result is None
    assert error == (
        "Open Food Facts request failed: Request timed out"
    )

def test_identify_product_invalid_json():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()
    mock_response.json.side_effect = (
        requests.exceptions.JSONDecodeError(
            "Invalid JSON", "", 0
        )
    )

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ):
        result, error = identify_product("bread.jpg")

    assert result is None
    assert error == (
        "Open Food Facts returned an invalid JSON response."
    )


def test_identify_product_invalid_response_structure():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()
    mock_response.json.return_value = []

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ):
        result, error = identify_product("bread.jpg")

    assert result is None
    assert error == (
        "Open Food Facts returned an invalid response structure."
    )


def test_identify_product_invalid_product_structure():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "product": []
    }

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ):
        result, error = identify_product("bread.jpg")

    assert result is None
    assert error == (
        "Open Food Facts returned an invalid product structure."
    )

def test_identify_product_missing_optional_metadata():
    mock_barcode = {
        "barcode": "041220053667",
        "barcode_type": "UPC_A"
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "product": {
            "product_name": "Honey Wheat"
        }
    }

    with patch(
        "modules.barcode_lookup.decode_barcode",
        return_value=(mock_barcode, None)
    ), patch(
        "modules.barcode_lookup.requests.get",
        return_value=mock_response
    ):
        result, error = identify_product("bread.jpg")

    assert error is None

    assert result == {
        "barcode": "041220053667",
        "barcode_type": "UPC_A",
        "product_name": "Honey Wheat",
        "brand": None,
        "source_category": None,
        "quantity": None,
        "product_data_source": "Open Food Facts",
        "input_method": "barcode_image",
        "user_confirmed": False
    }

   