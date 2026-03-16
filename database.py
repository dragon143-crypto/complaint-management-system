import sqlite3

def get_connection():
    conn = sqlite3.connect("complaints.db", check_same_thread=False)
    create_tables(conn)
    return conn

def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        complaint TEXT,
        status TEXT
    )
    """)

    conn.commit()