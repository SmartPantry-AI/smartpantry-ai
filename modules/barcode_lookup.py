# SmartPantry AI
# Role 2: Barcode and Product Data
# Phase 2 - Product Identification Pipeline

import cv2
import requests


def decode_barcode(image_path):
    """Detect and decode a barcode from an image."""

    # Load the barcode image
    image = cv2.imread(image_path)

    if image is None:
        return None, "Image could not be loaded."

    # Create the OpenCV barcode detector
    detector = cv2.barcode.BarcodeDetector()

    # Decode the barcode and identify its type
    success, decoded_info, decoded_type, points = (
        detector.detectAndDecodeWithType(image)
    )

    if not success or not decoded_info:
        return None, "No barcode detected."

    # Store the first detected barcode
    barcode = decoded_info[0]
    barcode_type = decoded_type[0]

    return {
        "barcode": barcode,
        "barcode_type": barcode_type
    }, None


def identify_product(image_path):
    """Identify a food product and return a standardized SmartPantry record."""

    # Step 1: Decode the barcode
    barcode_result, barcode_error = decode_barcode(image_path)

    if barcode_error:
        return None, barcode_error

    barcode_value = barcode_result["barcode"]
    barcode_type = barcode_result["barcode_type"]

    # Step 2: Look up the barcode in Open Food Facts
    url = (
        f"https://world.openfoodfacts.org/"
        f"api/v3/product/{barcode_value}.json"
    )

    headers = {
        "User-Agent": "SmartPantryAI/1.0 (student capstone project)"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        return None, f"Open Food Facts request failed: {error}"

    # Step 3: Check whether Open Food Facts found the product
    if "product" not in data:
        return None, "Product not found. Manual entry required."

    product = data["product"]

    # Step 4: Create the standardized SmartPantry record
    pantry_record = {
        "barcode": barcode_value,
        "barcode_type": barcode_type,
        "product_name": product.get("product_name"),
        "brand": product.get("brands"),
        "source_category": product.get("categories"),
        "quantity": product.get("quantity"),
        "product_data_source": "Open Food Facts",
        "input_method": "barcode_image",
        "user_confirmed": False
    }

    return pantry_record, None
