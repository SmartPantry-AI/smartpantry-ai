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


def check_recall(product_name, recalls_df, brand=None, upc=None):
    """
    Returns a structured recall result.
    """

    product_name = product_name.lower().strip()

    # UPC Match (Highest Confidence)
    if upc:

        for _, row in recalls_df.iterrows():

            recall_upc = str(row.get("upc", "")).strip()

            if recall_upc and recall_upc == str(upc):

                return {
                    "status": "RECALLED",
                    "source": "FDA",
                    "matched_product": row["product_description"]
                }

    # Exact Product Match
    for description in recalls_df["product_description"].fillna(""):

        description = description.lower()

        if description == product_name:

            return {
                "status": "RECALLED",
                "source": "FDA",
                "matched_product": description
            }

    # Brand + Product Match
    if brand:

        brand = brand.lower().strip()

        for description in recalls_df["product_description"].fillna(""):

            description = description.lower()

            if (
                brand in description
                and product_name in description
            ):
                return {
                    "status": "POSSIBLE_MATCH",
                    "source": "FDA",
                    "matched_product": description
                }

    # Product-Only Match
    for description in recalls_df["product_description"].fillna(""):

        description = description.lower()

        if product_name in description:

            return {
                "status": "POSSIBLE_MATCH",
                "source": "FDA",
                "matched_product": description
            }

    return {
        "status": "CLEAR",
        "source": None,
        "matched_product": None
    }


if __name__ == "__main__":

    API_KEY = input("Enter FDA API Key: ")

    recalls = get_fda_recalls(
        API_KEY,
        search_term="milk",
        limit=20
    )

    print("Records Found:", len(recalls))

    print(
        check_recall(
            "chocolate",
            recalls,
            brand="elite"
        )
    )

    print(
        check_recall(
            "banana",
            recalls
        )
    )
