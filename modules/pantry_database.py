import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "data" / "smartpantry.db"

def get_connection():
    """Create a connection to the SmartPantry SQLite database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    return connection

def create_pantry_table():
    """Create the pantry table if it does not already exist."""
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS pantry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL
            )
        """)

        cursor = connection.execute(
            """
            SELECT LOWER(name), unit, SUM(quantity), COUNT(*)
            FROM pantry
            GROUP BY LOWER(name), unit
            HAVING COUNT(*) > 1
            """
        )

        duplicate_groups = cursor.fetchall()

        for name, unit, total_quantity, record_count in duplicate_groups:
            print(
                f"Duplicate found: {name}, "
                f"{total_quantity} {unit}, "
                f"{record_count} records"
            )

            connection.execute(
                """
                UPDATE pantry
                SET quantity = ?
                WHERE id = (
                    SELECT MIN(id)
                    FROM pantry
                    WHERE lower(name) = ? AND unit = ?
                )
                """,
                (total_quantity, name, unit)
            )

            connection.execute(
                """
                DELETE FROM pantry
                WHERE LOWER(name) = ? AND unit = ?
                AND id != (
                    SELECT MIN(id)
                    FROM pantry
                    WHERE lower(name) = ? AND unit = ?
                )
                """,
                (name, unit, name, unit)
            )

        connection.commit()
    finally:
        connection.close()


def save_pantry_item(name, quantity, unit):
    """Save a pantry ingredient to the SQLite database."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT id, quantity
            FROM pantry
            WHERE LOWER(name) = LOWER(?) AND unit = ?
            """,
            (name, unit)
        )

        existing_item = cursor.fetchone()

        if existing_item:
            item_id, existing_quantity = existing_item

            new_quantity = existing_quantity + quantity

            connection.execute(
                """
                UPDATE pantry
                SET quantity = ?
                WHERE id = ?
                """,
                (new_quantity, item_id)
            )
        else:
            connection.execute(
                """
                INSERT INTO pantry (name, quantity, unit)
                VALUES (?, ?, ?)
                """,
                (name, quantity, unit)
        )

        connection.commit()

    finally:
        connection.close()


def load_pantry_items():
    """Load saved pantry ingredients from SQLite."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            "SELECT name, quantity, unit FROM pantry ORDER BY id"
        )

        rows = cursor.fetchall()

        items = [
            {
                "name": row[0],
                "quantity": row[1],
                "unit": row[2]
            }
            for row in rows
        ]

        return items

    finally:
        connection.close()


