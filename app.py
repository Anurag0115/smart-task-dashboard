import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import date
from init_db import init_db
from auth import authenticate
from style import style_priority

# Initialize DB
init_db()

st.set_page_config("📋 Smart Task Dashboard", layout="wide")

# -------------------- LOGIN ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(u, p):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# -------------------- MAIN APP ---------------------
st.title("📋 Smart Task Dashboard")

conn = sqlite3.connect("tasks.db")
df = pd.read_sql("SELECT * FROM tasks", conn)

# ------- THEME SWITCH -------
theme = st.sidebar.radio("🌙 Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("<style>body { background-color: #1e1e1e; color: white }</style>", unsafe_allow_html=True)

# ------- SEARCH BAR -------
search = st.text_input("🔎 Search by employee/project")
if search:
    df = df[df["employee"].str.contains(search, case=False) | df["project"].str.contains(search, case=False)]

# ------- KPI METRICS -------
st.markdown("### 📊 Summary")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Tasks", len(df))
k2.metric("✅ Completed", len(df[df.status == "Completed"]))
k3.metric("🚧 In Progress", len(df[df.status == "In Progress"]))
k4.metric("⏳ Pending", len(df[df.status == "Pending"]))

# ------- ADD TASK -------
st.markdown("### ➕ Add New Task")
with st.form("add_task"):
    c1, c2, c3 = st.columns(3)
    with c1:
        project = st.text_input("Project")
        employee = st.text_input("Employee")
    with c2:
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    with c3:
        start_date = st.date_input("Start Date", value=date.today())
        due_date = st.date_input("Due Date")
        completed_date = st.date_input("Completed Date") if status == "Completed" else ""

    if st.form_submit_button("Add Task"):
        conn.execute("INSERT INTO tasks (project, employee, status, start_date, due_date, completed_date, priority) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (project, employee, status, str(start_date), str(due_date), str(completed_date), priority))
        conn.commit()
        st.success("✅ Task Added")
        st.rerun()

# ------- FILTERING -------
st.markdown("### 🔍 Filter Tasks")
f1, f2, f3 = st.columns(3)
with f1:
    status_filter = st.multiselect("Status", df["status"].unique())
with f2:
    employee_filter = st.multiselect("Employee", df["employee"].unique())
with f3:
    project_filter = st.multiselect("Project", df["project"].unique())

fdf = df.copy()
if status_filter:
    fdf = fdf[fdf["status"].isin(status_filter)]
if employee_filter:
    fdf = fdf[fdf["employee"].isin(employee_filter)]
if project_filter:
    fdf = fdf[fdf["project"].isin(project_filter)]

# ------- OVERDUE HIGHLIGHT -------
def highlight(row):
    if row["status"] != "Completed" and row["due_date"] < str(date.today()):
        return ['background-color: #ffcccc'] * len(row)
    return [''] * len(row)

# ------- STYLE TASKS -------
df_disp = fdf.copy()
df_disp["priority"] = df_disp["priority"].apply(style_priority)
st.dataframe(df_disp.style.apply(highlight, axis=1), use_container_width=True)

# ------- DOWNLOAD -------
st.download_button("⬇️ Download CSV", fdf.to_csv(index=False), "filtered_tasks.csv", "text/csv")

# ------- EDIT TASK -------
st.markdown("### ✏️ Edit Task Status")
task_ids = df["id"].tolist()
eid = st.selectbox("Task ID", task_ids)
new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"], key="edit")
if st.button("Update Status"):
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, eid))
    conn.commit()
    st.success("✅ Status Updated")
    st.rerun()

# ------- DELETE TASK -------
st.markdown("### 🗑️ Delete Task")
did = st.selectbox("Delete Task ID", task_ids, key="delete")
if st.button("Delete Task"):
    conn.execute("DELETE FROM tasks WHERE id = ?", (did,))
    conn.commit()
    st.warning("⚠️ Task Deleted")
    st.rerun()

# ------- VISUALIZATIONS -------
st.markdown("### 📈 Visual Reports")
v1, v2 = st.columns(2)
with v1:
    proj_data = df["project"].value_counts().reset_index()
    proj_data.columns = ["project", "count"]
    fig1 = px.pie(proj_data, names="project", values="count", title="Project Distribution")
    st.plotly_chart(fig1, use_container_width=True)
with v2:
    emp_data = df["employee"].value_counts().reset_index()
    emp_data.columns = ["employee", "count"]
    fig2 = px.bar(emp_data, x="employee", y="count", title="Employee Productivity")
    st.plotly_chart(fig2, use_container_width=True)

conn.close()
