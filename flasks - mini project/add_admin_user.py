import sqlite3
import os

DB_PATH = 'app.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, email, password, is_verified) 
        VALUES ('admin', 'admin@example.com', 'admin', 1)
    """)
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    user = cursor.fetchone()
    print(f"Admin user: {user}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
print("Admin user setup complete! Login with username: admin, password: admin")

