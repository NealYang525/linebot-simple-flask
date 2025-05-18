from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("✅ 收到 LINE 的訊息！")
    return "OK", 200  # 很重要！LINE 要求 200 才會成功

@app.route("/", methods=["GET"])
def home():
    return "Skyona LINE Bot 正在運行中！"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

