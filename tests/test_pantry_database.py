import sqlite3
from modules import pantry_database


def test_database_connection(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    connection = pantry_database.get_connection()

    assert isinstance(connection, sqlite3.Connection)
    assert test_database.exists()

    connection.close()


def test_create_pantry_table(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    connection = pantry_database.get_connection()

    try:
        result = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'pantry'
        """).fetchone()

        assert result is not None
        assert result[0] == "pantry"

    finally:
        connection.close()


def test_save_pantry_item(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    pantry_database.save_pantry_item("spinach", 2, "bag")

    connection = pantry_database.get_connection()

    try:
        result = connection.execute(
            "SELECT name, quantity, unit FROM pantry"
        ).fetchone()

        assert result == ("spinach", 2, "bag")

    finally:
        connection.close()


def test_load_pantry_items(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()
    pantry_database.save_pantry_item("spinach", 2, "bag")

    items = pantry_database.load_pantry_items()

    assert items == [
        {
            "name": "spinach",
            "quantity": 2,
            "unit": "bag"
        }
    ]


def test_duplicate_pantry_items_are_combined(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    pantry_database.save_pantry_item("carrots", 3, "bag")
    pantry_database.save_pantry_item("carrots", 2, "bag")

    items = pantry_database.load_pantry_items()

    assert len(items) == 1
    assert items[0]["name"] == "carrots"
    assert items[0]["quantity"] == 5
    assert items[0]["unit"] == "bag"


def test_save_pantry_item_combines_duplicates(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    pantry_database.save_pantry_item("carrots", 3, "bag")
    pantry_database.save_pantry_item("carrots", 2, "bag")

    items = pantry_database.load_pantry_items()

    assert len(items) == 1
    assert items[0]["name"] == "carrots"
    assert items[0]["quantity"] == 5
    assert items[0]["unit"] == "bag"

def test_existing_duplicate_records_are_combined(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    connection = pantry_database.get_connection()

    try:
        connection.executemany(
            """
            INSERT INTO pantry (name, quantity, unit)
            VALUES (?, ?, ?)
            """,
            [
                ("carrots", 3, "bag"),
                ("carrots", 2, "bag")
            ]
        )
        connection.commit()
    finally:
        connection.close()

    pantry_database.create_pantry_table()

    items = pantry_database.load_pantry_items()

    assert len(items) == 1
    assert items[0]["name"] == "carrots"
    assert items[0]["quantity"] == 5
    assert items[0]["unit"] == "bag"


    pantry_database.create_pantry_table()

    items_after_second_run = pantry_database.load_pantry_items()

    assert len(items_after_second_run) == 1
    assert items_after_second_run[0]["quantity"] == 5

def test_existing_duplicates_ignore_capitalization(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    connection = pantry_database.get_connection()

    try:
        connection.executemany(
            """
            INSERT INTO pantry (name, quantity, unit)
            VALUES (?, ?, ?)
            """,
            [
                ("carrots", 3, "bag"),
                ("Carrots", 2, "bag")
            ]
        )
        connection.commit()
    finally:
        connection.close()

    pantry_database.create_pantry_table()

    items = pantry_database.load_pantry_items()

    assert len(items) == 1
    assert items[0]["quantity"] == 5

def test_save_pantry_item_ignores_capitalization(tmp_path, monkeypatch):
    test_database = tmp_path / "smartpantry_test.db"

    monkeypatch.setattr(
        pantry_database,
        "DATABASE_PATH",
        test_database
    )

    pantry_database.create_pantry_table()

    pantry_database.save_pantry_item("carrots", 3, "bag")
    pantry_database.save_pantry_item("Carrots", 2, "bag")

    items = pantry_database.load_pantry_items()

    assert len(items) == 1
    assert items[0]["quantity"] == 5
    assert items[0]["unit"] == "bag"


    





