from unittest.mock import MagicMock
from modules.supabase_pantry import load_user_pantry
from modules.supabase_pantry import load_user_pantry, add_pantry_item

import pytest

from modules.supabase_pantry import (
    load_user_pantry,
    add_pantry_item,
    delete_user_pantry_item,
    update_pantry_item_quantity,
)


def test_load_user_pantry():
    """Verify that pantry items are retrieved correctly."""

    mock_client = MagicMock()

    expected_items = [
        {"id": 1, "name": "Apple", "quantity": 2, "unit": "each"},
        {"id": 2, "name": "Carrot", "quantity": 3, "unit": "each"},
    ]

    mock_client.table.return_value.select.return_value.order.return_value.execute.return_value.data = expected_items

    result = load_user_pantry(mock_client)

    assert result == expected_items

    mock_client.table.assert_called_once_with("pantry_items")
    mock_client.table.return_value.select.assert_called_once_with("*")
    mock_client.table.return_value.select.return_value.order.assert_called_once_with("id")


def test_load_user_pantry_empty():
    """Verify that an empty pantry returns an empty list."""

    mock_client = MagicMock()

    mock_client.table.return_value.select.return_value.order.return_value.execute.return_value.data = []

    result = load_user_pantry(mock_client)

    assert result == []


def test_add_pantry_item():
    """Verify that an ingredient is saved for the authenticated user."""

    mock_client = MagicMock()

    mock_client.auth.get_user.return_value.user.id = "test-user-123"

    expected_item = {
        "user_id": "test-user-123",
        "name": "Apple",
        "quantity": 2,
        "unit": "item",
    }

    mock_client.table.return_value.insert.return_value.execute.return_value.data = [
        expected_item
    ]

    result = add_pantry_item(mock_client, "Apple", 2, "item")

    mock_client.auth.get_user.assert_called_once_with()
    mock_client.table.assert_called_once_with("pantry_items")
    mock_client.table.return_value.insert.assert_called_once_with(expected_item)

    assert result == [expected_item]


def test_add_pantry_item_database_error():
    """Verify that database errors are not silently ignored."""

    mock_client = MagicMock()
    mock_client.auth.get_user.return_value.user.id = "test-user-123"

    mock_client.table.return_value.insert.return_value.execute.side_effect = (
        RuntimeError("Database insert failed")
    )

    with pytest.raises(RuntimeError, match="Database insert failed"):
        add_pantry_item(mock_client, "Apple", 2, "item")


def test_delete_user_pantry_item():
    """Verify that the correct pantry item is deleted."""

    mock_client = MagicMock()

    deleted_item = {
        "id": 5,
        "name": "Apple",
        "quantity": 2,
        "unit": "item",
    }

    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
        deleted_item
    ]

    result = delete_user_pantry_item(mock_client, 5)

    mock_client.table.assert_called_once_with("pantry_items")
    mock_client.table.return_value.delete.assert_called_once_with()
    mock_client.table.return_value.delete.return_value.eq.assert_called_once_with(
        "id", 5
    )

    assert result == [deleted_item]


def test_delete_user_pantry_item_not_accessible():
    """Verify that no deleted records returns an empty list."""

    mock_client = MagicMock()

    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []

    result = delete_user_pantry_item(mock_client, 999)

    assert result == []

    mock_client.table.return_value.delete.return_value.eq.assert_called_once_with(
        "id", 999
    )

def test_update_pantry_item_quantity():
    """Verify that the correct pantry item's quantity is updated."""

    mock_client = MagicMock()

    updated_item = {
        "id": 5,
        "name": "Apple",
        "quantity": 5,
        "unit": "item",
    }

    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        updated_item
    ]

    result = update_pantry_item_quantity(mock_client, 5, 5)

    mock_client.table.assert_called_once_with("pantry_items")

    mock_client.table.return_value.update.assert_called_once_with(
        {"quantity": 5}
    )

    mock_client.table.return_value.update.return_value.eq.assert_called_once_with(
        "id", 5
    )

    assert result == [updated_item]

def test_update_pantry_item_quantity_not_accessible():
    """Verify that an inaccessible item returns no updated records."""

    mock_client = MagicMock()

    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []

    result = update_pantry_item_quantity(mock_client, 999, 5)

    assert result == []

    mock_client.table.return_value.update.assert_called_once_with(
        {"quantity": 5}
    )

    mock_client.table.return_value.update.return_value.eq.assert_called_once_with(
        "id", 999
    )
    
        
