import psycopg2
import os

# Get Render's PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgresSQL
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Create users table in PostgreSQL
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    app_password TEXT
);
""")

conn.commit()
cur.close()
conn.close()
print("✅ JD PostgreSQL database initialized successfully.")

