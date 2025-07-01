from flask import Flask, render_template, request, jsonify, session
from jd_core import handle_command

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session handling

@app.route("/")
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    command = data["command"]
    response = handle_command(command)

    actions = {}
    if "youtube" in command.lower() or "play" in command.lower():
        actions["youtube_song"] = command.replace("play", "").replace("on youtube", "").strip()

    # Save to session chat history
    history = session.get("chat_history", [])
    history.append({"command": command, "response": response})
    session["chat_history"] = history

    return jsonify({"response": response, "actions": actions})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")



