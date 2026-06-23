#!/usr/bin/env python3
"""
Database helper for pipeline-multimodale-automatica-per-backup.
Provides functions to initialize the database and insert metadata.
"""

import sqlite3
from pathlib import Path

def get_base_dir():
    """Return the base directory of the project (parent of scripts)."""
    return Path(__file__).resolve().parent.parent

def get_db_path():
    """Return the path to the SQLite database."""
    return get_base_dir() / "data" / "metadata.db"

def init_db():
    """Initialize the database by executing the schema.sql script."""
    base_dir = get_base_dir()
    schema_path = base_dir / "scripts" / "schema.sql"
    db_path = get_db_path()

    # Ensure the data directory exists
    db_path.parent.mkdir(exist_ok=True)

    with open(schema_path, 'r') as f:
        schema = f.read()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()

def insert_metadata(path, type, json_blob):
    """
    Insert a media record and its metadata into the database.

    Args:
        path (str): Absolute or relative path to the media file.
        type (str): Type of media (e.g., 'image', 'audio').
        json_blob (str): JSON string containing metadata.

    Returns:
        int: The ID of the inserted metadata record.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Insert into media table (ignore if already exists)
        cursor.execute(
            """
            INSERT OR IGNORE INTO media (path, type)
            VALUES (?, ?)
            """,
            (path, type)
        )

        # Get the media_id (whether inserted or already existing)
        cursor.execute(
            "SELECT id FROM media WHERE path = ?",
            (path,)
        )
        row = cursor.fetchone()
        if row is None:
            # This should not happen because we just inserted or ignored
            raise Exception(f"Failed to retrieve media_id for path: {path}")
        media_id = row[0]

        # Insert into metadata table
        cursor.execute(
            """
            INSERT INTO metadata (media_id, json_blob)
            VALUES (?, ?)
            """,
            (media_id, json_blob)
        )

        metadata_id = cursor.lastrowid
        conn.commit()
        return metadata_id
    finally:
        conn.close()

if __name__ == "__main__":
    # When run directly, initialize the database and run a simple test.
    print("Initializing database...")
    init_db()
    print("Database initialized.")

    # Example usage
    test_path = "/tmp/test.jpg"
    test_type = "image"
    test_json = '{"width": 800, "height": 600, "format": "JPEG"}'
    try:
        metadata_id = insert_metadata(test_path, test_type, test_json)
        print(f"Inserted metadata with ID: {metadata_id}")
    except Exception as e:
        print(f"Error during test insertion: {e}")