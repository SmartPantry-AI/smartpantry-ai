def load_user_pantry(client):
    """Retrieve pantry items nelonging to the authenticated user."""
    response = (
        client.table("pantry_items")
        .select("*")
        .order("id")
        .execute()
    )

    return response.data

def add_pantry_item(client, name, quantity, unit):
    """Save a pantry item for the authenticated user."""

    user_response = client.auth.get_user()
    user_id = user_response.user.id

    item_data = {
        "user_id": user_id,
        "name": name,
        "quantity": quantity,
        "unit": unit,
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

