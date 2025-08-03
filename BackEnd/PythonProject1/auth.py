from flask import Blueprint, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

auth = Blueprint("auth", __name__)

# ✅ Use DATABASE_URL from Render environment (set automatically)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@auth.route("/update_app_password", methods=["GET", "POST"])
def update_app_password():
    if not session.get("logged_in"):
        return redirect("/auth/login")

    if request.method == "POST":
        new_app_password = request.form["app_password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET app_password = %s WHERE username = %s",
            (new_app_password, session["username"])
        )
        conn.commit()
        cur.close()
        conn.close()

        session["app_password"] = new_app_password
        return render_template("update_app_password.html", message="Gmail App Password updated successfully.")

    return render_template("update_app_password.html")

# ✅ Ensure the users table exists
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
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

init_db()


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["logged_in"] = True
            session["username"] = user[1]
            session["email"] = user[3]
            session["app_password"] = user[4]
            return redirect("/")
        else:
            return render_template("auth.html", message="Invalid credentials", mode="login")

    return render_template("auth.html", mode="login")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        app_password = request.form["app_password"]

        hashed_pw = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, password, email, app_password)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed_pw, email, app_password))
            conn.commit()
            cur.close()
            conn.close()

            session["logged_in"] = True
            session["username"] = username
            session["email"] = email
            session["app_password"] = app_password
            return redirect("/")
        except psycopg2.errors.UniqueViolation:
            return render_template("auth.html", message="Username already exists", mode="register")
        except Exception as e:
            return render_template("auth.html", message="Error: " + str(e), mode="register")

    return render_template("auth.html", mode="register")
