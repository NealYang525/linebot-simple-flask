from flask import Flask, request
import requests
import json
import openai
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

# 機密變數從環境讀取
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def home():
    return "Skyona Bot + GPT + Gmail is running!", 200

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "Webhook is active", 200

    body = request.get_json()
    print("✅ 收到 Webhook:", json.dumps(body, indent=2))

    for event in body.get("events", []):
        if event["type"] == "message":
            msg_type = event["message"]["type"]
            reply_token = event["replyToken"]

            if msg_type == "text":
                user_msg = event["message"]["text"]
                ai_reply = chatgpt(user_msg)
                reply(reply_token, ai_reply)

                if need_notify(user_msg):
                    send_email("客服通知", f"收到客戶問題：{user_msg}\nAI 回覆：{ai_reply}")

            elif msg_type == "image":
                reply(reply_token, "收到圖片囉！")

    return "OK", 200

def reply(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, data=json.dumps(body))
    print("✅ 回應結果：", response.status_code, response.text)

def chatgpt(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"AI 回覆失敗：{e}"

def need_notify(text):
    keywords = ["壞掉", "異常", "故障", "客服", "問題", "報修"]
    return any(kw in text for kw in keywords)

def send_email(subject, content):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
            print("✅ 已寄出通知 email")
    except Exception as e:
        print("❌ email 寄送失敗：", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
