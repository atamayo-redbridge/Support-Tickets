import sqlite3
import bcrypt

# 🔹 Initialize Database
def init_db():
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('user', 'co-admin', 'admin')) NOT NULL DEFAULT 'user',
        must_reset INTEGER DEFAULT 0
    )
    """)

    # Tickets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT CHECK(status IN ('Open', 'In Progress', 'Closed')) NOT NULL DEFAULT 'Open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_email) REFERENCES users(email) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()

# 🔹 Get User Data
def get_user(email):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# 🔹 Create a New User
def create_user(first_name, last_name, email, role):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    
    # Generate a default password
    default_password = "Welcome123!"
    hashed_password = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password, role, must_reset) VALUES (?, ?, ?, ?, ?, 1)",
            (first_name, last_name, email, hashed_password, role)
        )
        conn.commit()
        return {"message": "User Created Successfully", "password": default_password}
    except sqlite3.IntegrityError:
        return {"message": "Email already exists"}
    finally:
        conn.close()

# 🔹 Update Password
def update_password(email, new_password):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cursor.execute("UPDATE users SET password=?, must_reset=0 WHERE email=?", (hashed_password, email))
    conn.commit()
    conn.close()

# 🔹 Create a Ticket
def create_ticket(user_email, title, description):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (user_email, title, description, status) VALUES (?, ?, ?, 'Open')",
        (user_email, title, description)
    )
    conn.commit()
    conn.close()

# 🔹 Fetch Tickets
def get_tickets(user_email, role):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    if role == "admin":
        cursor.execute("SELECT * FROM tickets")
    else:
        cursor.execute("SELECT * FROM tickets WHERE user_email=?", (user_email,))
    tickets = cursor.fetchall()
    conn.close()
    return tickets

# 🔹 Update Ticket Status
def update_ticket_status(ticket_id, status):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()


