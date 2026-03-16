import streamlit as st
import pandas as pd
import uuid
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

# ---------------------
# CREATE TABLES IF NOT EXISTS
# ---------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Students(
student_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
department TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Categories(
category_id INTEGER PRIMARY KEY AUTOINCREMENT,
category_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Complaints(
complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
tracking_id TEXT,
student_id INTEGER,
category_id INTEGER,
complaint_text TEXT,
status TEXT DEFAULT 'Pending',
complaint_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# default admin
cursor.execute("""
INSERT OR IGNORE INTO Users(username,password,role)
VALUES('admin','admin123','admin')
""")

conn.commit()

# ---------------------

st.set_page_config(
page_title="Student Complaint System",
page_icon="🎓",
layout="wide"
)

# ---------------------
# SESSION STATES
# ---------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------------------
# LOGIN PAGE
# ---------------------

if not st.session_state.logged_in:

    st.title("🎓 Student Complaint Management System")

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            query = """
            SELECT * FROM Users
            WHERE username=? AND password=?
            """

            user = pd.read_sql(query, conn, params=(username,password))

            if not user.empty:

                st.session_state.logged_in = True
                st.session_state.role = user.iloc[0]["role"]

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Credentials")

    st.stop()

# ---------------------
# SIDEBAR
# ---------------------

st.sidebar.title("Navigation")

if st.sidebar.button("📊 Dashboard"):
    st.session_state.page="Dashboard"

if st.sidebar.button("🧑 Register Student"):
    st.session_state.page="Register"

if st.sidebar.button("📝 Submit Complaint"):
    st.session_state.page="Submit"

if st.sidebar.button("🔍 Track Complaint"):
    st.session_state.page="Track"

if st.sidebar.button("📋 View Complaints"):
    st.session_state.page="View"

if st.sidebar.button("⚙ Admin Panel"):
    st.session_state.page="Admin"

menu = st.session_state.page

# ---------------------
# DASHBOARD
# ---------------------

if menu=="Dashboard":

    st.title("📊 Complaint Dashboard")

    total = pd.read_sql("SELECT COUNT(*) c FROM Complaints",conn)
    pending = pd.read_sql("SELECT COUNT(*) c FROM Complaints WHERE status='Pending'",conn)
    progress = pd.read_sql("SELECT COUNT(*) c FROM Complaints WHERE status='In Progress'",conn)
    resolved = pd.read_sql("SELECT COUNT(*) c FROM Complaints WHERE status='Resolved'",conn)

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total",total.iloc[0]["c"])
    col2.metric("Pending",pending.iloc[0]["c"])
    col3.metric("In Progress",progress.iloc[0]["c"])
    col4.metric("Resolved",resolved.iloc[0]["c"])

    chart = pd.read_sql("""
    SELECT status,COUNT(*) total
    FROM Complaints
    GROUP BY status
    """,conn)

    st.bar_chart(chart.set_index("status"))

# ---------------------
# REGISTER STUDENT
# ---------------------

elif menu=="Register":

    st.title("🧑 Student Registration")

    name = st.text_input("Name")
    email = st.text_input("Email")
    dept = st.text_input("Department")

    if st.button("Register Student"):

        cursor.execute(
        "INSERT INTO Students(name,email,department) VALUES(?,?,?)",
        (name,email,dept)
        )

        conn.commit()

        st.success("Student Registered")

# ---------------------
# SUBMIT COMPLAINT
# ---------------------

elif menu=="Submit":

    st.title("📝 Submit Complaint")

    students = pd.read_sql("SELECT student_id,name FROM Students",conn)
    categories = pd.read_sql("SELECT category_id,category_name FROM Categories",conn)

    if students.empty:
        st.warning("No students registered")
        st.stop()

    if categories.empty:

        cursor.execute("""
        INSERT INTO Categories(category_name)
        VALUES('Hostel'),('Food'),('Transport'),('Academic')
        """)
        conn.commit()

        categories = pd.read_sql("SELECT category_id,category_name FROM Categories",conn)

    student = st.selectbox("Student",students["student_id"])
    category = st.selectbox("Category",categories["category_id"])

    complaint = st.text_area("Complaint")

    if st.button("Submit Complaint"):

        tracking_id = str(uuid.uuid4())[:8]

        cursor.execute("""
        INSERT INTO Complaints(tracking_id,student_id,category_id,complaint_text,status)
        VALUES(?,?,?,?,?)
        """,(tracking_id,student,category,complaint,"Pending"))

        conn.commit()

        st.success(f"Complaint Submitted. Tracking ID: {tracking_id}")

# ---------------------
# TRACK
# ---------------------

elif menu=="Track":

    st.title("🔍 Track Complaint")

    track = st.text_input("Tracking ID")

    if track:

        df = pd.read_sql("""
        SELECT tracking_id,complaint_text,status,complaint_date
        FROM Complaints
        WHERE tracking_id=?
        """,conn,params=(track,))

        st.dataframe(df)

# ---------------------
# VIEW
# ---------------------

elif menu=="View":

    st.title("📋 All Complaints")

    df = pd.read_sql("""
    SELECT
    Complaints.tracking_id,
    Students.name,
    Categories.category_name,
    Complaints.complaint_text,
    Complaints.status
    FROM Complaints
    JOIN Students ON Students.student_id=Complaints.student_id
    JOIN Categories ON Categories.category_id=Complaints.category_id
    """,conn)

    st.dataframe(df)

# ---------------------
# ADMIN PANEL
# ---------------------

elif menu=="Admin":

    st.title("⚙ Admin Panel")

    df = pd.read_sql(
    "SELECT complaint_id,complaint_text,status FROM Complaints",
    conn
    )

    st.dataframe(df)

    cid = st.number_input("Complaint ID",step=1)

    status = st.selectbox(
    "Update Status",
    ["Pending","In Progress","Resolved"]
    )

    if st.button("Update Status"):

        cursor.execute(
        "UPDATE Complaints SET status=? WHERE complaint_id=?",
        (status,cid)
        )

        conn.commit()

        st.success("Status Updated")