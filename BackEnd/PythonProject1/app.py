import os
import psycopg2
from flask import Flask, render_template, request, jsonify, session, redirect

from auth import auth
from jd_core import handle_command

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

app.register_blueprint(auth, url_prefix="/auth")

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn


# noinspection PyUnreachableCode
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect("/auth/login")
    show_update_password = not bool(session.get("app_password"))
    return render_template("index.html", show_update_password=show_update_password)

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

@app.route("/process", methods=["POST"])
def process():
    if not session.get("logged_in"):
        return jsonify({"response": "Please log in first."})

    data = request.get_json()
    command = data["command"]
    response = handle_command(command)

    actions = {}
    if "youtube" in command.lower() or "play" in command.lower():
        song = command.lower().replace("play", "").replace("on youtube", "").strip()
        actions["youtube_song"] = song

    return jsonify({"response": response, "actions": actions})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/auth/login")

if __name__ == "__main__":
    app.run(debug=True)





