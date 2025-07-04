import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Updated schema: includes 'name' field
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

conn.commit()
conn.close()

print("Database and users table created.")

