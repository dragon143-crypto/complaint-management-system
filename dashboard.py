import streamlit as st
import pandas as pd
from database import get_connection

def show_dashboard():

    conn = get_connection()

    st.header("Complaint Analytics")

    query = """
    SELECT status, COUNT(*) as total
    FROM Complaints
    GROUP BY status
    """

    df = pd.read_sql(query, conn)

    st.bar_chart(df.set_index("status"))