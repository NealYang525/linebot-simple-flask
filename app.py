from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("✅ 收到 LINE 發來的訊息")
    return "OK", 200  # 一定要回傳 200 給 LINE 平台

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

