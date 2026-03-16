import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=LAPTOP-QQOC2OUE;"
        "DATABASE=StudentComplaintDB;"
        "Trusted_Connection=yes;"
    )
    return conn