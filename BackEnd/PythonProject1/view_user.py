import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("SELECT id, name, email FROM users")
rows = c.fetchall()

print("Registered Users:")
for row in rows:
    print(f"ID: {row[0]} | Name: {row[1]} | Email: {row[2]}")

conn.close()
