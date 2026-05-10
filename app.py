import os
import json
import hmac
import hashlib
import base64
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from line_service import reply_line_message, push_line_message
from stock_checker import check_once

load_dotenv()

app = Flask(__name__)

USER_FILE = "users.json"
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")


def load_users():
    if not os.path.exists(USER_FILE):
        return []
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_user(user_id: str):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def verify_signature(body: bytes, signature: str) -> bool:
    if not LINE_CHANNEL_SECRET:
        return True

    hash_value = hmac.new(
        LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode("utf-8")
    return hmac.compare_digest(expected_signature, signature)


@app.route("/", methods=["GET"])
def home():
    return "LINE Stock Alert Bot is running."


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_data()
    signature = request.headers.get("X-Line-Signature", "")

    if not verify_signature(body, signature):
        return jsonify({"error": "invalid signature"}), 403

    data = request.get_json(silent=True) or {}

    for event in data.get("events", []):
        event_type = event.get("type")
        source = event.get("source", {})
        user_id = source.get("userId")
        reply_token = event.get("replyToken")

        if user_id:
            save_user(user_id)

        if event_type == "follow" and reply_token:
            reply_line_message(
                reply_token,
                "已加入好友並完成綁定。之後可以主動推播台股監控通知給你。"
            )

        elif event_type == "message":
            message = event.get("message", {})
            text = message.get("text", "").strip()

            if text in ["綁定", "bind", "Bind", "BIND"]:
                reply_line_message(reply_token, "已完成綁定。你之後會收到台股監控通知。")

            elif text in ["測試", "test", "Test", "TEST"]:
                push_line_message(user_id, "LINE Bot 測試通知成功。")
                reply_line_message(reply_token, "已發送一則測試 Push 通知。")

            elif text in ["檢查", "check", "Check", "CHECK"]:
                result_text = check_once(send=False)
                reply_line_message(reply_token, result_text[:4800])

            else:
                reply_line_message(
                    reply_token,
                    "可用指令：\n1. 綁定\n2. 測試\n3. 檢查\n\n正式監控可由 Render Background Worker 或排程服務執行。"
                )

    return jsonify({"status": "ok"})


@app.route("/manual-check", methods=["GET"])
def manual_check():
    admin_token = os.getenv("ADMIN_TOKEN", "")
    query_token = request.args.get("token", "")

    if admin_token and query_token != admin_token:
        return jsonify({"error": "unauthorized"}), 401

    result = check_once(send=True)
    return jsonify({"result": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
