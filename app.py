import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from init_db import init_db  # ⬅️ Automatically initializes the DB if not present

# Initialize the DB (only first time)
init_db()

# App config
st.set_page_config(page_title="Smart Task Insight Dashboard", layout="wide")
st.title("📊 Smart Task Insight Dashboard")

# Connect and fetch data
def get_data():
    conn = sqlite3.connect("tasks.db")
    df = pd.read_sql_query("SELECT * FROM tasks", conn, parse_dates=["start_date", "due_date", "completed_date"])
    conn.close()
    return df

df = get_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")
employees = st.sidebar.multiselect("Select Employee(s)", options=df["employee"].unique(), default=df["employee"].unique())
projects = st.sidebar.multiselect("Select Project(s)", options=df["project"].unique(), default=df["project"].unique())
status = st.sidebar.multiselect("Select Status", options=df["status"].unique(), default=df["status"].unique())

# Apply filters
filtered_df = df[
    (df["employee"].isin(employees)) &
    (df["project"].isin(projects)) &
    (df["status"].isin(status))
]

st.subheader("📁 Filtered Task Data")
st.dataframe(filtered_df, use_container_width=True)

# KPIs
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tasks", len(filtered_df))
col2.metric("Completed", (filtered_df["status"] == "Completed").sum())
col3.metric("In Progress", (filtered_df["status"] == "In Progress").sum())
col4.metric("Pending", (filtered_df["status"] == "Pending").sum())

# Overdue Tasks
today = datetime.today()
filtered_df["due_date"] = pd.to_datetime(filtered_df["due_date"])
filtered_df["completed_date"] = pd.to_datetime(filtered_df["completed_date"])
overdue_tasks = filtered_df[
    (filtered_df["status"] != "Completed") &
    (filtered_df["due_date"] < today)
]

with st.expander("⚠️ Overdue Tasks"):
    st.dataframe(overdue_tasks[["id", "project", "employee", "due_date"]])

# Pie Chart
fig1 = px.pie(filtered_df, names="status", title="Task Distribution by Status")
st.plotly_chart(fig1, use_container_width=True)

# ✅ Fixed Bar Chart
emp_count = filtered_df["employee"].value_counts().reset_index()
emp_count.columns = ["employee", "count"]
fig2 = px.bar(emp_count, x="employee", y="count", title="Tasks per Employee",
              labels={"employee": "Employee", "count": "Task Count"})
st.plotly_chart(fig2, use_container_width=True)

# Timeline Chart
filtered_df["start_date"] = pd.to_datetime(filtered_df["start_date"])
fig3 = px.timeline(filtered_df, x_start="start_date", x_end="due_date", y="employee",
                   color="status", title="Task Timeline")
fig3.update_yaxes(autorange="reversed")
st.plotly_chart(fig3, use_container_width=True)

# Download CSV
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered Data", csv, "filtered_tasks.csv", "text/csv")
