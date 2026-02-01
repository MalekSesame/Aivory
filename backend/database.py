import sqlite3
from pathlib import Path

DB_PATH = Path("documents.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_document(filename: str, filepath: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (filename, filepath) VALUES (?, ?)",
        (filename, filepath)
    )
    conn.commit()
    conn.close()
