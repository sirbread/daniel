import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import dotenv

dotenv.load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

# too tired to deal with ratelimits
channel_id = "C099KGNC1GB"

app = Flask(__name__)

@app.route("/send-slack", methods=["POST"])
def send_message():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "no text"}), 400

    text = data["text"]

    try:
        response = client.chat_postMessage(channel=channel_id, text=text)
        result = {"channel": channel_id, "ok": True, "ts": response["ts"]}
    except SlackApiError as e:
        result = {"channel": channel_id, "ok": False, "error": e.response["error"]}

    return jsonify({"ok": True, "results": [result]})

@app.route("/list-slack-channels", methods=["GET"])
def list_channels():
    try:
        response = client.conversations_info(channel=channel_id)
        channel = response["channel"]
        channel_data = {"id": channel["id"], "name": channel["name"]}
    except SlackApiError as e:
        return jsonify({"ok": False, "error": e.response["error"]}), 500

    return jsonify({"ok": True, "channels": [channel_data]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009)
