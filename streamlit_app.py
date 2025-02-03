import datetime
import random
import os
import shutil
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Set app title and layout
st.set_page_config(page_title="IT Support Ticketing System", page_icon="🎫", layout="wide")

# Ensure upload directory exists
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Page Title
st.title("🎫 IT Support Ticketing System")
st.write("Easily track, manage, and resolve IT-related issues in one place!")

# Initialize Ticket Data in Session
if "df" not in st.session_state:
    np.random.seed(42)

    issue_descriptions = [
        "Network connectivity issues", "Software crash on startup", "Printer not responding",
        "Email server downtime", "Data backup failure", "Login authentication problems",
        "Website performance slow", "Security vulnerability identified", "Hardware failure",
        "Employee unable to access shared files", "Database connection failure",
        "Mobile app sync issues", "VoIP phone system problems", "VPN connection issues",
        "System updates causing errors", "File server low on storage",
        "Intrusion detection system alerts", "Inventory system errors", 
        "Customer data not loading in CRM", "Collaboration tool notifications failing"
    ]

    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182)) for _ in range(100)],
        "Attachment": [None] * 100  # Placeholder for file attachments
    }
    df = pd.DataFrame(data)
    st.session_state.df = df

# 📌 Sidebar Navigation
st.sidebar.image("https://img.icons8.com/ios-filled/50/000000/ticket.png", width=50)
menu = st.sidebar.radio("Navigation", ["📬 Dashboard", "📩 Submit Ticket", "📋 View Tickets"])

# 🔹 Dashboard
if menu == "📬 Dashboard":
    st.header("📊 IT Ticket Statistics")
    
    col1, col2, col3 = st.columns(3)

    num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
    num_in_progress = len(st.session_state.df[st.session_state.df.Status == "In Progress"])
    num_closed = len(st.session_state.df[st.session_state.df.Status == "Closed"])

    col1.metric(label="🟢 Open Tickets", value=num_open_tickets)
    col2.metric(label="🟡 In Progress", value=num_in_progress)
    col3.metric(label="🔴 Closed", value=num_closed)

    # 📊 Ticket Status Chart
    st.write("##### 📅 Ticket Status Over Time")
    status_chart = (
        alt.Chart(st.session_state.df)
        .mark_bar()
        .encode(
            x="month(Date Submitted):O",
            y="count():Q",
            color="Status:N"
        )
        .configure_legend(orient="bottom", titleFontSize=14, labelFontSize=14)
    )
    st.altair_chart(status_chart, use_container_width=True, theme="streamlit")

    # 📊 Priority Distribution
    st.write("##### 🔥 Ticket Priority Breakdown")
    priority_chart = (
        alt.Chart(st.session_state.df)
        .mark_arc()
        .encode(theta="count():Q", color="Priority:N")
        .properties(height=300)
        .configure_legend(orient="bottom", titleFontSize=14, labelFontSize=14)
    )
    st.altair_chart(priority_chart, use_container_width=True, theme="streamlit")

# 🔹 Submit Ticket (With File Attachments)
elif menu == "📩 Submit Ticket":
    st.header("📩 Submit a New Ticket")
    
    with st.form("add_ticket_form"):
        issue = st.text_area("📝 Describe the issue", placeholder="Enter detailed issue description...")
        priority = st.selectbox("⚠️ Priority Level", ["High", "Medium", "Low"])
        uploaded_file = st.file_uploader("📎 Attach a file (optional)", type=["png", "jpg", "pdf", "txt", "log"])
        submitted = st.form_submit_button("🎟 Submit Ticket")
    
    if submitted:
        new_ticket_id = f"TICKET-{int(max(st.session_state.df.ID).split('-')[1]) + 1}"
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = None

        if uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
        
        df_new = pd.DataFrame([{
            "ID": new_ticket_id,
            "Issue": issue,
            "Status": "Open",
            "Priority": priority,
            "Date Submitted": today,
            "Attachment": file_path if uploaded_file else None
        }])

        st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)
        st.success(f"✅ Ticket {new_ticket_id} created successfully!")

# 🔹 View & Manage Tickets (With Attachments)
elif menu == "📋 View Tickets":
    st.header("📋 All Support Tickets")

    # Ticket Filters
    col1, col2, col3 = st.columns(3)
    
    search_term = col1.text_input("🔍 Search by Issue", "")
    status_filter = col2.selectbox("📌 Filter by Status", ["All", "Open", "In Progress", "Closed"])
    priority_filter = col3.selectbox("⚠️ Filter by Priority", ["All", "High", "Medium", "Low"])

    filtered_df = st.session_state.df

    if search_term:
        filtered_df = filtered_df[filtered_df["Issue"].str.contains(search_term, case=False, na=False)]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df["Priority"] == priority_filter]

    # Editable Ticket Table with Attachment Links
    for index, row in filtered_df.iterrows():
        with st.expander(f"🎫 {row['ID']} - {row['Issue']}"):
            st.write(f"📅 **Submitted:** {row['Date Submitted']}")
            st.write(f"⚠️ **Priority:** {row['Priority']}")
            st.write(f"🔄 **Status:** {row['Status']}")
            if row["Attachment"]:
                st.write(f"📎 **Attachment:** [{os.path.basename(row['Attachment'])}](uploads/{os.path.basename(row['Attachment'])})")
            st.markdown("---")

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Powered by Redbridge IT Group")
