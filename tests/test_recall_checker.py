import pandas as pd


def run_tests():

    recalls = pd.DataFrame([
        {
            "product_description": "Milk Chocolate Rice Cakes",
            "upc": "123456789"
        }
    ])

    print(
        "Test 1:",
        check_recall(
            "Chocolate Rice Cakes",
            recalls,
            upc="123456789"
        )
    )

    print(
        "Test 2:",
        check_recall(
            "chocolate",
            recalls,
            brand="elite"
        )
    )

    print(
        "Test 3:",
        check_recall(
            "banana",
            recalls
        )
    )


if __name__ == "__main__":
    run_tests()
  
