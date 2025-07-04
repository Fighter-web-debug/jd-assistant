import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Corrected query
c.execute("SELECT id, username, email FROM users")

users = c.fetchall()

for user in users:
    print(user)

conn.close()

