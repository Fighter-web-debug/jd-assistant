import os
import psycopg2
import urllib.parse
from flask import Flask, render_template, request, jsonify, session, redirect
from jd_core import handle_command
from auth import auth

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

# Register blueprint
app.register_blueprint(auth, url_prefix="/auth")

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect("/auth/login")
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





