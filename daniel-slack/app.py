import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_BOT_TOKEN)

app = Flask(__name__)

def get_joined_channels():
    channels = []
    cursor = None
    while True:
        try:
            response = client.conversations_list( # ugh took way to long to get the perms right -_-
                types="public_channel,private_channel",
                exclude_archived=True,
                limit=200,
                cursor=cursor
            )
            for ch in response["channels"]:
                if ch.get("is_member"):
                    channels.append({"id": ch["id"], "name": ch["name"]})
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        except SlackApiError as e:
            print(f"Error fetching channels: {e.response['error']}")
            break
    return channels

@app.route("/send-slack", methods=["POST"])
def send_message():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "no text"}), 400

    text = data["text"]
    channels = get_joined_channels()
    results = []

    for ch in channels:
        try:
            response = client.chat_postMessage(channel=ch["id"], text=text)
            results.append({"channel": ch["name"], "ok": True, "ts": response["ts"]})
        except SlackApiError as e:
            results.append({"channel": ch["name"], "ok": False, "error": e.response["error"]})

    return jsonify({"ok": True, "results": results})

@app.route("/list-slack-channels", methods=["GET"])
def list_channels():
    channels = get_joined_channels()
    return jsonify({"ok": True, "channels": channels})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009)
