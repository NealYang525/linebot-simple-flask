from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("收到 LINE 的訊息！")
    return "OK"

if __name__ == "__main__":
    app.run()
