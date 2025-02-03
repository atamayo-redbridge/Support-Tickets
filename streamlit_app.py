import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
from backend import get_user, update_password, create_user

# Set Page Title & Layout
st.set_page_config(page_title="IT Ticketing System", page_icon="🎫", layout="wide")

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["email"] = None
    st.session_state["role"] = None

# 🔹 LOGIN FORM
def login():
    st.sidebar.title("🔐 Login")
    email = st.sidebar.text_input("📧 Email")
    password = st.sidebar.text_input("🔑 Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        user = get_user(email)
        if user and bcrypt.checkpw(password.encode(), user[4].encode()):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["role"] = user[5]  # Role
            st.session_state["must_reset"] = user[6]  # Password Reset Required
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid email or password")

# 🔹 PASSWORD RESET FORM
def password_reset():
    st.subheader("🔄 Reset Your Password")
    new_password = st.text_input("🔑 Enter New Password", type="password")
    confirm_password = st.text_input("🔑 Confirm New Password", type="password")
    reset_button = st.button("Reset Password")

    if reset_button:
        if new_password == confirm_password:
            update_password(st.session_state["email"], new_password)
            st.success("✅ Password Reset Successful! Please Login Again.")
            st.session_state["logged_in"] = False
            st.experimental_rerun()
        else:
            st.error("Passwords do not match!")

# 🔹 DASHBOARD BASED ON ROLE
def dashboard():
    st.sidebar.title("🎫 IT Ticketing System")

    if st.session_state["role"] == "admin":
        menu = st.sidebar.radio("Navigation", ["📩 Create User", "📋 Manage Tickets", "📊 Admin Dashboard"])

        if menu == "📩 Create User":
            st.header("👤 Create a New User")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["user", "co-admin", "admin"])

            if st.button("Create User"):
                result = create_user(first_name, last_name, email, role)
                st.success(f"✅ {result['message']} Default Password: `{result['password']}`")
        
        elif menu == "📋 Manage Tickets":
            st.header("📋 View & Manage All Tickets")
            st.write("🔹 **Admin can see & update all tickets here...**")
            # Add ticket management functionalities...

        elif menu == "📊 Admin Dashboard":
            st.header("📊 Ticket Statistics & Overview")
            # Add dashboard metrics...

    elif st.session_state["role"] == "co-admin":
        st.header("🛠️ Co-Admin Ticket Dashboard")
        st.write("🔹 **Co-Admins can manage certain tickets...**")
        # Co-Admin functionalities...

    else:
        st.header("🎟 My Tickets")
        st.write("🔹 **View and manage your own tickets...**")
        # User-specific functionalities...

    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False, "email": None, "role": None}))
    st.experimental_rerun()

# 🔹 AUTHENTICATION LOGIC
if not st.session_state["logged_in"]:
    login()
else:
    if st.session_state["must_reset"] == 1:
        password_reset()
    else:
        dashboard()
