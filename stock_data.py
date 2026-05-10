import os
from datetime import datetime, timedelta
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

FINMIND_TOKEN = os.getenv("FINMIND_TOKEN", "")


def get_tw_stock_daily_price(stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": start_date,
        "end_date": end_date,
    }
    if FINMIND_TOKEN:
        params["token"] = FINMIND_TOKEN

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != 200:
        raise RuntimeError(f"FinMind 回傳錯誤：{data}")

    df = pd.DataFrame(data.get("data", []))
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    for col in ["Trading_Volume", "open", "max", "min", "close", "spread", "Trading_turnover"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values("date").reset_index(drop=True)


def get_recent_price(stock_id: str, analysis_date: str, lookback_days: int = 35) -> pd.DataFrame:
    end_dt = datetime.strptime(analysis_date, "%Y/%m/%d")
    start_dt = end_dt - timedelta(days=lookback_days)
    return get_tw_stock_daily_price(
        stock_id=stock_id,
        start_date=start_dt.strftime("%Y-%m-%d"),
        end_date=end_dt.strftime("%Y-%m-%d"),
    )
