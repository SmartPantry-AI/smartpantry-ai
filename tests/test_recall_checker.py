import pandas as pd
from modules.recall_checker import check_recall


def run_tests():

    recalls = pd.DataFrame([
        {
            "product_description": "Milk Chocolate Rice Cakes",
            "upc": "123456789"
        }
    ])

    # Test 1: UPC Match
    result = check_recall(
        "Chocolate Rice Cakes",
        recalls,
        upc="123456789"
    )

    assert result["status"] == "RECALLED"
    print("✅ Test 1 Passed: UPC Match")

    # Test 2: Brand + Product Match
    result = check_recall(
        "chocolate",
        recalls,
        brand="elite"
    )

    assert result["status"] == "POSSIBLE_MATCH"
    print("✅ Test 2 Passed: Brand Match")

    # Test 3: No Match
    result = check_recall(
        "banana",
        recalls
    )

    assert result["status"] == "CLEAR"
    print("✅ Test 3 Passed: Clear Result")


if __name__ == "__main__":
    run_tests()
    # Test 4: Unknown Product
    result = check_recall(
        "laptop",
        recalls
    )

    assert result["status"] == "CLEAR"
    print("✅ Test 4 Passed: Unknown Product")

    # Test 5: Product-Only Match
    result = check_recall(
        "milk",
        recalls
    )

    assert result["status"] == "POSSIBLE_MATCH"
    print("✅ Test 5 Passed: Product Match")
