def load_user_pantry(client):
    """Retrieve pantry items nelonging to the authenticated user."""
    response = (
        client.table("pantry_items")
        .select("*")
        .order("id")
        .execute()
    )

    return response.data

def add_pantry_item(
    client,
    name,
    quantity,
    unit,
    purchase_date=None,
    expiration_date=None,
    storage_location=None,
    prepared_date=None,
    brand=None,
    upc=None,
    lot_code=None,
    food_classification=None,
    preparation_state=None,
    package_state=None,
    opened_date=None,
    thawed_date=None,
):
    """Save a pantry item for the authenticated user."""

    user_response = client.auth.get_user()
    user_id = user_response.user.id

    item_data = {
        "user_id": user_id,
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "purchase_date": purchase_date,
        "expiration_date": expiration_date,
        "storage_location": storage_location,
        "prepared_date": prepared_date,
        "brand": brand,
        "upc": upc,
        "lot_code": lot_code,
        "food_classification": food_classification,
        "preparation_state": preparation_state,
        "package_state": package_state,
        "opened_date": opened_date,
        "thawed_date": thawed_date,
        
    }

    response = (
        client.table("pantry_items")
        .insert(item_data)
        .execute()
    )

    return response.data

def delete_user_pantry_item(client, item_id):
    """Delete a pantry item using the authenticated user's client"""

    response = (
        client.table("pantry_items")
        .delete()
        .eq("id", item_id)
        .execute()
    )

    return response.data

def update_pantry_item_quantity(client, item_id, quantity):
    """Update the quantity of a pantry item."""

    response = (
        client.table("pantry_items")
        .update({"quantity": quantity})
        .eq("id", item_id)
        .execute()
    )

    return response.data

