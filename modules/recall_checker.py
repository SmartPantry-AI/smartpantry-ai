import pandas as pd
import requests


def get_fda_recalls(api_key, search_term="milk", limit=5):

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


def check_recall(product_name, recalls_df, brand=None):

    product_name = product_name.lower().strip()

    # Exact match
    for description in recalls_df["product_description"].fillna(""):

        description = description.lower()

        if description == product_name:
            return "RECALLED"

    # Brand + Product Match
    if brand:

        brand = brand.lower().strip()

        for description in recalls_df["product_description"].fillna(""):

            description = description.lower()

            if (
                brand in description
                and product_name in description
            ):
                return "POSSIBLE_MATCH"

    # Product-only partial match
    for description in recalls_df["product_description"].fillna(""):

        description = description.lower()

        if product_name in description:
            return "POSSIBLE_MATCH"

    return "CLEAR"


if __name__ == "__main__":

    API_KEY = input("Enter FDA API Key: ")

    recalls = get_fda_recalls(
        API_KEY,
        search_term="milk",
        limit=20
    )

    print("Records Found:", len(recalls))

   print(
    "Elite Chocolate:",
    check_recall(
        "chocolate",
        recalls,
        brand="elite"
    )
)

print(
    "Milk:",
    check_recall(
        "milk",
        recalls
    )
)

print(
    "Banana:",
    check_recall(
        "banana",
        recalls
    )
)
