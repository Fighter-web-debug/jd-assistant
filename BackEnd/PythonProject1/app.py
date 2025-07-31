import sqlite3
import urllib.parse

from flask import Flask, render_template, request, jsonify, session, redirect
from jd_core import handle_command
from auth import auth  # Blueprint for login/register

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Register blueprint
app.register_blueprint(auth, url_prefix="/auth")

def get_db_connection():
    conn = sqlite3.connect('jd_users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect("/auth/login")  # Corrected path
    return render_template("index.html")

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
        youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song)}"
        actions["youtube_url"] = youtube_url

    return jsonify({"response": response, "actions": actions})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/auth/login")

if __name__ == "__main__":
    app.run(debug=True)




