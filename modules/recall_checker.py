import pandas as pd
import requests


def get_fda_recalls(api_key, search_term="milk", limit=5):
    """
    Pull recall records from openFDA.
    """

    url = "https://api.fda.gov/food/enforcement.json"

    params = {
        "api_key": api_key,
        "search": f"product_description:{search_term}",
        "limit": limit,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        results = response.json().get("results", [])
        return pd.json_normalize(results)

    return pd.DataFrame()


def check_recall(product_name, recalls_df):
    """
    Returns:
        RECALLED
        CLEAR
    """

    matches = recalls_df[
        recalls_df["product_description"]
        .str.contains(product_name, case=False, na=False)
    ]

    if len(matches) > 0:
        return "RECALLED"

    return "CLEAR"


if __name__ == "__main__":
    print("Testing Recall Checker...")

    test_data = pd.DataFrame([
        {
            "product_description": "Milk Chocolate Rice Cakes"
        },
        {
            "product_description": "Frozen Pizza"
        }
    ])

    print("Milk:", check_recall("milk", test_data))
    print("Banana:", check_recall("banana", test_data))

