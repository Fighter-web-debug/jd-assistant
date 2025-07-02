from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from jd_core import handle_command
from auth import auth  # Your auth blueprint
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Register auth blueprint
app.register_blueprint(auth)

# SQLite DB path
DB_PATH = "users.db"

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/auth")
    return render_template("index.html")

@app.route("/auth")
def auth_page():
    return render_template("auth.html")

@app.route("/process", methods=["POST"])
def process():
    if not session.get("user_id"):
        return jsonify({"response": "Please log in first."})

    data = request.get_json()
    command = data["command"]
    response = handle_command(command)

    actions = {}
    if "youtube" in command.lower() or "play" in command.lower():
        actions["youtube_song"] = command.replace("play", "").replace("on youtube", "").strip()

    return jsonify({"response": response, "actions": actions})


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE email = ? AND password = ?", (email, password))
        row = cur.fetchone()
        con.close()

        if row:
            session["user_id"] = row[0]
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Invalid credentials."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"})


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            con.close()
            return jsonify({"success": False, "message": "Email already exists."})

        cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        con.commit()
        user_id = cur.lastrowid
        con.close()

        session["user_id"] = user_id
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/auth")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")




