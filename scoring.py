import pandas as pd


def score_short_term(df: pd.DataFrame):
    if df.empty or len(df) < 20:
        return 0, ["資料不足"]

    last = df.iloc[-1]
    prev = df.iloc[-2]
    score_items = []

    def add(cond, name):
        if bool(cond):
            score_items.append(name)

    add(last["close"] > last["MA5"], "收盤站上5日線")
    add(last["close"] > last["MA10"], "收盤站上10日線")
    add(last["K"] > last["D"] and prev["K"] <= prev["D"], "KD黃金交叉")
    add(last["RSI14"] > 50, "RSI站上50")
    add(last["MACD_HIST"] > 0, "MACD柱狀體為正")
    add(last["MACD_HIST"] > prev["MACD_HIST"], "MACD柱狀體轉強")
    add(last["close"] > prev["close"] and last["Trading_Volume"] > df["Trading_Volume"].tail(5).mean(), "上漲放量")
    add(last["OBV"] > last["OBV_MA5"], "OBV站上5日均線")
    add(last["close"] > df.iloc[-6]["close"], "近5日漲幅為正")
    add(last["RSI14"] < 80, "RSI未過熱")

    return len(score_items), score_items


def score_long_term(df: pd.DataFrame):
    if df.empty or len(df) < 20:
        return 0, ["資料不足"]

    last = df.iloc[-1]
    score_items = []

    def add(cond, name):
        if bool(cond):
            score_items.append(name)

    add(last["close"] > last["MA20"], "收盤站上20日線")
    add(last["MA5"] > last["MA10"], "5日線高於10日線")
    add(last["MA10"] > last["MA20"], "10日線高於20日線")
    add(df["close"].tail(10).mean() > df["close"].head(10).mean(), "近月均價趨勢向上")
    add(df["Trading_Volume"].tail(5).mean() > df["Trading_Volume"].tail(20).mean() * 0.8, "量能維持")
    add(last["MACD"] > last["MACD_SIGNAL"], "MACD多方")
    add(last["OBV"] > df["OBV"].tail(20).mean(), "OBV中期偏強")
    add(last["RSI14"] > 45, "RSI中期不弱")

    score_items.append("EPS/ROE/毛利率/估值尚未串接，暫不給基本面分")
    return len([x for x in score_items if "尚未串接" not in x]), score_items


def classify(short_score: int, long_score: int):
    if short_score >= 8 and long_score >= 8:
        return "短長線皆強"
    if short_score >= 8:
        return "偏短線波段"
    if long_score >= 8:
        return "偏長線布局"
    if short_score >= 6 or long_score >= 6:
        return "可觀察"
    return "暫不建議"
