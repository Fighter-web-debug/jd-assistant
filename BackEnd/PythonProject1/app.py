import os
import psycopg2
from flask import Flask, render_template, request, jsonify, session, redirect

from auth import auth, init_db   # <-- import init_db here
from jd_core import handle_command


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

app.register_blueprint(auth, url_prefix="/auth")


DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# ⬇️ SAFE place to initialize DB (not during import!)
def create_app():
    with app.app_context():
        try:
            init_db()
            print("Database initialized successfully.")
        except Exception as e:
            print("DB init failed or skipped:", e)
    return app


@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect("/auth/login")

    show_update_password = not bool(session.get("app_password"))
    return render_template("index.html", show_update_password=show_update_password)


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


# Start app safely
create_app()

if __name__ == "__main__":
    app.run(debug=True)




