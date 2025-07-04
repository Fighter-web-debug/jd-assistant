from flask import Flask, render_template, request, jsonify, session, redirect
from jd_core import handle_command
from auth import auth  # Your auth blueprint

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Register auth blueprint
app.register_blueprint(auth)

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect("/auth")
    return render_template("index.html")

@app.route("/auth")
def auth_page():
    return render_template("auth.html", mode="login")

@app.route("/process", methods=["POST"])
def process():
    if not session.get("logged_in"):
        return jsonify({"response": "Please log in first."})

    data = request.get_json()
    command = data["command"]
    response = handle_command(command)

    actions = {}
    if "youtube" in command.lower() or "play" in command.lower():
        actions["youtube_song"] = command.replace("play", "").replace("on youtube", "").strip()

    return jsonify({"response": response, "actions": actions})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")




