import sqlite3

def get_connection():
    conn = sqlite3.connect("complaints.db", check_same_thread=False)
    return conn