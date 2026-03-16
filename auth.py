import streamlit as st
import pandas as pd
from database import get_connection

def login():

    conn = get_connection()

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        query = """
        SELECT * FROM Users
        WHERE username=? AND password=?
        """

        user = pd.read_sql(query, conn, params=(username, password))

        if not user.empty:
            st.session_state["logged_in"] = True
            st.session_state["role"] = user.iloc[0]["role"]

            st.success("Login Successful")

            st.rerun()   # 🔴 important line

        else:
            st.error("Invalid Login")