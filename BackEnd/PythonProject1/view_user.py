from flask import Blueprint, render_template, session
import sqlite3

view_user = Blueprint("view_user", __name__)

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Corrected query
c.execute("SELECT id, username, email FROM users")

users = c.fetchall()

for user in users:
    print(user)

conn.close()

@view_user.route("/user")
def user_profile():
    if not session.get("logged_in"):
        return redirect("/auth/login")

    return render_template("user_profile.html",
                           username=session.get("username"),
                           email=session.get("email"))

