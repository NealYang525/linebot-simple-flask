from flask import Flask, request
import requests
import json

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'VnZN3UjLpWpNdk7fNz1EnggkK4AiOi6e7Vdsj0rpj07Rn/TUEPkr2atTkebuezATuHGJAjl9VTrRKaNtsin/WD0Et6o9sXOr9F2hGFZ9q2w1MAK85p+WN1N8aR3euYvVfnW+AFvmNbFzPyFDf0YnOwdB04t89/1O/w1cDnyilFU='

@app.route("/", methods=["GET"])
def home():
    return "Skyona Bot is running!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook is active.", 200

    if request.method == "POST":
        print("✅ 收到 LINE 傳來的 Webhook")
        body = request.get_json()
        print(json.dumps(body, indent=2))

        for event in body.get("events", []):
            if event["type"] == "message":
                msg_type = event["message"]["type"]
                reply_token = event["replyToken"]

                if msg_type == "text":
                    user_message = event["message"]["text"]
                    reply_text = f"你說的是：{user_message}"
                    reply(reply_token, reply_text)

                elif msg_type == "image":
                    reply(reply_token, "收到圖片囉 📷！")

        return "OK", 200

def reply(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    body = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": text
        }]
    }

    response = requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        data=json.dumps(body)
    )

    print("✅ 回應結果：", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
