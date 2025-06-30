from flask import Flask, render_template, request, jsonify
from jd_core import handle_command

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    command = data["command"]
    response = handle_command(command)

    actions = {}
    if "youtube" in command.lower() or "play" in command.lower():
        actions["youtube_song"] = command.replace("play", "").replace("on youtube", "").strip()

    return jsonify({"response": response, "actions": actions})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


