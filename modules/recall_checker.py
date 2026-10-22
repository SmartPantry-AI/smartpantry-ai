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

    API_KEY = input("Enter FDA API Key: ")

    recalls = get_fda_recalls(
        API_KEY,
        search_term="milk",
        limit=20
    )

    print("Records Found:", len(recalls))

    print("Milk:", check_recall("milk", recalls))
    print("Banana:", check_recall("banana", recalls))

