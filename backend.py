import sqlite3
import bcrypt
import random
import string
from passlib.context import CryptContext

# Secure Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Connection
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Create Users Table (If Not Exists)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        must_reset_password INTEGER DEFAULT 1
    )
""")
conn.commit()

# Generate Random Password
def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

# Hash Password
def hash_password(password):
    return pwd_context.hash(password)

# Validate Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create New User (Admin Only)
def create_user(first_name, last_name, email, role="user"):
    password = generate_password()
    hashed_password = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, email, hashed_password, role),
        )
        conn.commit()
        return {"email": email, "password": password, "message": "User created successfully!"}
    except sqlite3.IntegrityError:
        return {"message": "Error: Email already exists!"}

# Fetch User by Email
def get_user(email):
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

# Update Password (After First Login)
def update_password(email, new_password):
    hashed_password = hash_password(new_password)
    cursor.execute("UPDATE users SET password = ?, must_reset_password = 0 WHERE email = ?", (hashed_password, email))
    conn.commit()
    return {"message": "Password updated successfully!"}

# Ensure Default Admin Exists
def create_default_admin():
    admin_email = "admin@example.com"
    admin_password = "Admin123!"  # Default Password
    hashed_password = hash_password(admin_password)

    cursor.execute("SELECT * FROM users WHERE email = ?", (admin_email,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password, role, must_reset_password) VALUES (?, ?, ?, ?, ?, ?)",
            ("Admin", "User", admin_email, hashed_password, "admin", 0),
        )
        conn.commit()
        print(f"✅ Default Admin Created: {admin_email} | Password: {admin_password}")

# Run Admin Creation Check
create_default_admin()

