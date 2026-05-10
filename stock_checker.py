import os
import json
from datetime import datetime
import pandas as pd

from stock_data import get_recent_price
from indicators import add_indicators
from scoring import score_short_term, score_long_term, classify
from line_service import push_line_message

USER_FILE = "users.json"
WATCHLIST_FILE = "watchlist.csv"


def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return pd.DataFrame(columns=["stock_id", "stock_name", "analysis_date", "target_change_pct"])
    return pd.read_csv(WATCHLIST_FILE, dtype={"stock_id": str})


def build_message(row, short_score, short_items, long_score, long_items, df):
    last = df.iloc[-1]
    stock_id = row["stock_id"]
    stock_name = row.get("stock_name", "")
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    conclusion = classify(short_score, long_score)

    return (
        f"📈 台股AI監控通知\n"
        f"{now}\n\n"
        f"{stock_id} {stock_name}\n"
        f"分析日收盤價：{last['close']}\n"
        f"短線分數：{short_score}/10\n"
        f"短線得分：{'、'.join(short_items[:10])}\n\n"
        f"長線分數：{long_score}/10\n"
        f"長線得分：{'、'.join(long_items[:10])}\n\n"
        f"綜合判定：{conclusion}"
    )


def check_once(send: bool = True):
    watchlist = load_watchlist()
    if watchlist.empty:
        return "watchlist.csv 是空的，請先填入股票。"

    users = load_users()
    messages = []

    for _, row in watchlist.iterrows():
        stock_id = str(row["stock_id"])
        analysis_date = str(row["analysis_date"]).replace("-", "/")

        try:
            df = get_recent_price(stock_id, analysis_date, lookback_days=35)
            if df.empty:
                messages.append(f"{stock_id} {row.get('stock_name','')}：查無資料")
                continue

            df = add_indicators(df)
            short_score, short_items = score_short_term(df)
            long_score, long_items = score_long_term(df)
            msg = build_message(row, short_score, short_items, long_score, long_items, df)
            messages.append(msg)

            should_notify = short_score >= 8 or long_score >= 8

            if send and should_notify and users:
                for user_id in users:
                    push_line_message(user_id, msg)

        except Exception as exc:
            messages.append(f"{stock_id} {row.get('stock_name','')}：錯誤 {exc}")

    return "\n\n---\n\n".join(messages)


if __name__ == "__main__":
    print(check_once(send=False))
