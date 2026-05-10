# 台股 LINE Bot 主動通知系統

## 功能

- LINE Webhook 接收使用者訊息
- 傳「綁定」後儲存 userId
- 使用 LINE Push API 主動推播
- 使用 FinMind 抓台股日線資料
- 計算 MA、RSI、MACD、KD、OBV
- 依短線與長線條件給分
- 可用 /manual-check 手動觸發分析與推播

## 本機測試

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Windows 啟動虛擬環境：

```bash
.venv\Scripts\activate
```

## Render Web Service

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn app:app
```

## LINE Webhook URL

```text
https://你的-render-service.onrender.com/webhook
```

## 手動觸發

```text
https://你的-render-service.onrender.com/manual-check?token=你的ADMIN_TOKEN
```

## 每 10 秒監控

Render Web Service 適合處理 LINE Webhook。
若要每 10 秒常駐監控，建議另外建立 Render Background Worker，Start Command 使用：

```bash
python run_monitor.py
```
