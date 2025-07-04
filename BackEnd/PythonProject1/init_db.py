import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# Correct schema with `username` included
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    app_password TEXT
)
''')

conn.commit()
conn.close()
print("✅ users.db recreated with correct schema.")


