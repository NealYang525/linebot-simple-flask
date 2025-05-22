from flask import Flask, request
import requests
import json
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 讀取環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

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
                    gpt_reply = ask_gpt(user_message)
                    reply(reply_token, gpt_reply)

                    if should_notify(user_message):
                        send_email_notification(user_message, gpt_reply)

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

def ask_gpt(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一個友善且懂機械維修的客服助理"},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return f"抱歉，AI 回覆發生錯誤：{str(e)}"

def should_notify(message):
    keywords = ["報修", "壞掉", "沒反應", "故障", "聯絡客服"]
    return any(kw in message for kw in keywords)

def send_email_notification(user_message, gpt_reply):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = "【AI客服通知】使用者可能需要協助"

    body = f"使用者訊息：{user_message}

AI 回覆內容：{gpt_reply}"
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ 已寄送客服通知 email")
    except Exception as e:
        print(f"❌ email 發送失敗：{str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
