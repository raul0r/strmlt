import streamlit as st
from datetime import datetime

# ---- Initialize project/task storage ----
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# ---- Helper function ----
def add_task(project, description, due_date, status):
    task = {
        'Project': project,
        'Description': description,
        'Due Date': due_date,
        'Status': status,
        'Created': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.tasks.append(task)

# ---- App Layout ----
st.title("📝 Project Tracker")

st.header("Add New Task")
with st.form(key="task_form"):
    project = st.text_input("Project Name")
    description = st.text_input("Task Description")
    due_date = st.date_input("Due Date")
    status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
    submit = st.form_submit_button("Add Task")
    if submit:
        add_task(project, description, str(due_date), status)
        st.success("Task added!")

st.header("All Tasks")
if st.session_state.tasks:
    for idx, task in enumerate(st.session_state.tasks):
        with st.expander(f"{task['Project']} - {task['Description']}"):
            st.write(f"**Due Date:** {task['Due Date']}")
            st.write(f"**Status:** {task['Status']}")
            st.write(f"**Created:** {task['Created']}")
            new_status = st.selectbox("Update Status", ["Not Started", "In Progress", "Completed"], index=["Not Started", "In Progress", "Completed"].index(task["Status"]), key=f"status_{idx}")
            if new_status != task['Status']:
                st.session_state.tasks[idx]['Status'] = new_status
                st.info("Status updated!")
else:
    st.info("No tasks added yet.")

# ---- Optional: Show tasks as a table ----
if st.session_state.tasks:
    st.header("Task Table")
    st.dataframe(st.session_state.tasks)
