from flask import Blueprint, request, render_template, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from jd_state import user_session

auth = Blueprint("auth", __name__)

# Ensure database and table
conn = sqlite3.connect("jd_users.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    app_password TEXT
)''')
conn.commit()
conn.close()

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["logged_in"] = True
            session["username"] = user[1]
            session["email"] = user[3]
            session["app_password"] = user[4]

            user_session["logged_in"] = True
            user_session["username"] = user[1]
            user_session["email"] = user[3]
            user_session["app_password"] = user[4]

            return redirect("/")  # ✅ Redirect to homepage after login
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
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, email, app_password) VALUES (?, ?, ?, ?)",
                      (username, hashed_pw, email, app_password))
            conn.commit()
            conn.close()
            
            session["logged_in"] = True
            session['username'] = username
            session['email'] = email
            return redirect("/")
        except sqlite3.IntegrityError:
            return render_template("auth.html", message="Username already exists", mode="register")

    return render_template("auth.html", mode="register")
