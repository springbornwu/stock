import time
from datetime import datetime
from stock_checker import check_once


def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False

    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = now.replace(hour=13, minute=30, second=0, microsecond=0)
    return start <= now <= end


def main():
    print("Stock monitor started.")
    while True:
        if is_market_open():
            print(datetime.now(), "checking stocks...")
            print(check_once(send=True))
        else:
            print(datetime.now(), "market closed.")
        time.sleep(10)


if __name__ == "__main__":
    main()
