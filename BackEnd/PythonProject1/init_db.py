import sqlite3

conn = sqlite3.connect('jd_users.db')  # creates the file if it doesn't exist
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    app_password TEXT
)
''')

conn.commit()
conn.close()
print("✅ JD database recreated successfully.")
