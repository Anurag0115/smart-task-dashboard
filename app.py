import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from init_db import init_db

# Initialize DB
init_db()

st.set_page_config("Smart Task Dashboard", layout="wide")
st.title("📋 Smart Task Dashboard")

# Connect to DB
conn = sqlite3.connect("tasks.db")
df = pd.read_sql_query("SELECT * FROM tasks", conn)

# ----- KPI METRICS -----
st.subheader("📊 Task Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tasks", len(df))
col2.metric("Completed", len(df[df["status"] == "Completed"]))
col3.metric("In Progress", len(df[df["status"] == "In Progress"]))
col4.metric("Pending", len(df[df["status"] == "Pending"]))

st.markdown("---")

# ----- ADD TASK FORM -----
st.subheader("➕ Add New Task")
with st.form("add_task_form"):
    project = st.text_input("Project")
    employee = st.text_input("Employee")
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
    start_date = st.date_input("Start Date")
    due_date = st.date_input("Due Date")
    completed_date = st.date_input("Completed Date") if status == "Completed" else ""
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    submitted = st.form_submit_button("Add Task")

    if submitted:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tasks (project, employee, status, start_date, due_date, completed_date, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project, employee, status, str(start_date), str(due_date), str(completed_date), priority))
        conn.commit()
        st.success("✅ Task added successfully!")

# ----- FILTER TASKS -----
st.subheader("🔍 Filter Tasks")
status_filter = st.multiselect("Filter by Status", options=df["status"].unique())
employee_filter = st.multiselect("Filter by Employee", options=df["employee"].unique())
project_filter = st.multiselect("Filter by Project", options=df["project"].unique())

filtered_df = df.copy()
if status_filter:
    filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
if employee_filter:
    filtered_df = filtered_df[filtered_df["employee"].isin(employee_filter)]
if project_filter:
    filtered_df = filtered_df[filtered_df["project"].isin(project_filter)]

st.dataframe(filtered_df, use_container_width=True)

# ----- CSV DOWNLOAD -----
st.download_button("⬇️ Download Filtered Tasks", data=filtered_df.to_csv(index=False),
                   file_name="filtered_tasks.csv", mime="text/csv")

# ----- UPDATE TASK -----
st.subheader("✏️ Update Task Status")
task_ids = df["id"].tolist()
selected_id = st.selectbox("Select Task ID to Update", task_ids)
new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"])

if st.button("Update Status"):
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, selected_id))
    conn.commit()
    st.success("✅ Task status updated!")

# ----- DELETE TASK -----
st.subheader("🗑️ Delete Task")
delete_id = st.selectbox("Select Task ID to Delete", task_ids, key="delete_id")
if st.button("Delete Task"):
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (delete_id,))
    conn.commit()
    st.warning(f"⚠️ Task {delete_id} deleted.")

# ----- CHARTS -----
st.subheader("📈 Visualizations")

col5, col6 = st.columns(2)

with col5:
    project_count = df["project"].value_counts().reset_index()
    project_count.columns = ["project", "count"]
    fig1 = px.pie(project_count, names="project", values="count", title="Tasks per Project")
    st.plotly_chart(fig1, use_container_width=True)

with col6:
    emp_count = df["employee"].value_counts().reset_index()
    emp_count.columns = ["employee", "count"]
    fig2 = px.bar(emp_count, x="employee", y="count", title="Tasks per Employee",
                  labels={"employee": "Employee", "count": "Task Count"})
    st.plotly_chart(fig2, use_container_width=True)

conn.close()
