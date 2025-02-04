import streamlit as st
import sqlite3
import bcrypt
from backend import get_user, update_password, create_user, get_tickets, create_ticket, update_ticket_status

# Set Page Title & Layout
st.set_page_config(page_title="IT Ticketing System", page_icon="🎫", layout="centered")

# 🔹 Ensure Session State is Initialized
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "email": None,
        "role": None,
        "must_reset": None
    })

# 🔹 LOGIN FUNCTION
def login():
    st.markdown("<h1 style='text-align: center;'>🎫 IT Ticketing System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Secure Login</h3>", unsafe_allow_html=True)

    # Centered Login Form
    with st.form(key="login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        user = get_user(email)
        if user and bcrypt.checkpw(password.encode(), user[4].encode()):  # Validate password
            st.session_state.update({
                "logged_in": True,
                "email": email,
                "role": user[5],
                "must_reset": user[6]
            })
            st.rerun()  # Ensure session updates
        else:
            st.error("❌ Invalid email or password")

# 🔹 PASSWORD RESET FUNCTION
def password_reset():
    st.markdown("<h1 style='text-align: center;'>🔄 Reset Your Password</h1>", unsafe_allow_html=True)

    email = st.session_state["email"]
    with st.form(key="reset_form"):
        new_password = st.text_input("🔑 New Password", type="password")
        confirm_password = st.text_input("🔑 Confirm New Password", type="password")
        reset_button = st.form_submit_button("Reset Password")

    if reset_button:
        if new_password == confirm_password:
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            update_password(email, hashed_password)  # Store hashed password
            st.success("✅ Password Reset Successful! Please Login Again.")
            st.session_state.update({"logged_in": False, "email": None})
            st.rerun()
        else:
            st.error("❌ Passwords do not match!")

# 🔹 DASHBOARD FUNCTION
def dashboard():
    st.sidebar.title("🎫 IT Ticketing System")

    if st.session_state["role"] == "admin":
        menu = st.sidebar.radio("Navigation", ["📩 Create User", "📋 Manage Tickets", "📊 Admin Dashboard"])

        if menu == "📋 Manage Tickets":
            st.header("📋 Manage Tickets")
            tickets = get_tickets(None, "admin")

            if tickets:
                for ticket in tickets:
                    with st.expander(f"🆔 {ticket[0]} | {ticket[2]} - {ticket[4]}"):
                        st.write(f"**Description:** {ticket[3]}")
                        st.write(f"**Status:** `{ticket[4]}`")

                        new_status = st.selectbox(f"Update Ticket {ticket[0]}", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(ticket[4]))
                        if st.button(f"Update Ticket {ticket[0]}"):
                            update_ticket_status(ticket[0], new_status)
                            st.success(f"✅ Ticket {ticket[0]} updated to `{new_status}`")
                            st.rerun()
            else:
                st.info("No tickets available.")

    elif st.session_state["role"] == "user":
        st.header("🎟 My Tickets")

        # Create a new ticket
        with st.form(key="ticket_form"):
            title = st.text_input("Ticket Title")
            description = st.text_area("Describe the Issue")
            submit_ticket = st.form_submit_button("Submit Ticket")

        if submit_ticket:
            create_ticket(st.session_state["email"], title, description)
            st.success("✅ Ticket Submitted Successfully!")
            st.rerun()

        # Display User Tickets
        tickets = get_tickets(st.session_state["email"], "user")
        if tickets:
            for ticket in tickets:
                with st.expander(f"🆔 {ticket[0]} | {ticket[2]} - {ticket[4]}"):
                    st.write(f"**Description:** {ticket[3]}")
                    st.write(f"**Status:** `{ticket[4]}`")
        else:
            st.info("No tickets submitted yet.")

    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.update({"logged_in": False, "email": None, "role": None})
        st.rerun()

# 🔹 AUTHENTICATION LOGIC
if not st.session_state["logged_in"]:
    login()
else:
    if st.session_state["must_reset"] == 1:
        password_reset()
    else:
        dashboard()
