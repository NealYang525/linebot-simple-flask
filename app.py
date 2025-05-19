from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Hello, this is Skyona test bot."

@app.route("/webhook", methods=["POST"])
def webhook():
    print("✅ 收到 LINE 傳來的 Webhook！")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
