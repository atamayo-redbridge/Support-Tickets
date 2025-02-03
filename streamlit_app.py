import streamlit as st
import sqlite3
import bcrypt
from backend import get_user, update_password, create_user

# Set Page Title & Layout
st.set_page_config(page_title="IT Ticketing System", page_icon="🎫", layout="centered")

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["email"] = None
    st.session_state["role"] = None
    st.session_state["must_reset"] = None  # Track password reset state

# 🔹 CENTERED LOGIN FORM
def login():
    st.markdown("<h1 style='text-align: center;'>🎫 IT Ticketing System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Secure Login</h3>", unsafe_allow_html=True)

    # Centered Container
    login_container = st.container()
    with login_container:
        st.markdown(
            """
            <style>
                div[data-testid="stBlockContainer"] {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔑 Password", type="password", key="login_password")
        login_button = st.button("Login")

        if login_button:
            user = get_user(email)
            if user and bcrypt.checkpw(password.encode(), user[4].encode()):
                # Update session state **before** rerunning
                st.session_state["logged_in"] = True
                st.session_state["email"] = email
                st.session_state["role"] = user[5]  # Role
                st.session_state["must_reset"] = user[6]  # Password Reset Required
                st.rerun()  # **Safe rerun**
            else:
                st.error("❌ Invalid email or password")

# 🔹 PASSWORD RESET FORM
def password_reset():
    st.markdown("<h1 style='text-align: center;'>🔄 Reset Your Password</h1>", unsafe_allow_html=True)

    email = st.session_state["email"]
    new_password = st.text_input("🔑 Enter New Password", type="password")
    confirm_password = st.text_input("🔑 Confirm New Password", type="password")
    reset_button = st.button("Reset Password")

    if reset_button:
        if new_password == confirm_password:
            update_password(email, new_password)
            st.success("✅ Password Reset Successful! Please Login Again.")
            st.session_state["logged_in"] = False  # Logout after reset
            st.rerun()
        else:
            st.error("❌ Passwords do not match!")

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

    elif st.session_state["role"] == "user":
        st.header("🎟 My Tickets")
        st.write("🔹 **View and manage your own tickets...**")

    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False, "email": None, "role": None}))
    st.rerun()  # Ensure logout updates session

# 🔹 AUTHENTICATION LOGIC
if not st.session_state["logged_in"]:
    login()
else:
    if st.session_state["must_reset"] == 1:
        password_reset()
    else:
        dashboard()
