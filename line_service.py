import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")


def _headers():
    if not LINE_CHANNEL_ACCESS_TOKEN:
        raise RuntimeError("缺少 LINE_CHANNEL_ACCESS_TOKEN，請在 .env 或 Render Environment 設定。")

    return {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def push_line_message(user_id: str, message: str):
    url = "https://api.line.me/v2/bot/message/push"
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message[:4900]}],
    }
    response = requests.post(url, headers=_headers(), json=payload, timeout=15)
    print("LINE push:", response.status_code, response.text)
    response.raise_for_status()
    return response


def reply_line_message(reply_token: str, message: str):
    url = "https://api.line.me/v2/bot/message/reply"
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message[:4900]}],
    }
    response = requests.post(url, headers=_headers(), json=payload, timeout=15)
    print("LINE reply:", response.status_code, response.text)
    response.raise_for_status()
    return response
