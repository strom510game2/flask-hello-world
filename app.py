from flask import Flask, jsonify
import requests
import datetime

app = Flask(__name__)

# 台積電
stock_symbol = "2330.TW"
stock_name = "台積電"


# 取得最新股價（Yahoo）
def get_stock_price():
    try:
        url = (
            "https://query1.finance.yahoo.com/v8/finance/chart/"
            + stock_symbol
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        result = data["chart"]["result"][0]

        price = result["meta"]["regularMarketPrice"]

        return float(price)

    except Exception as e:
        print("Price Error:", e)
        return None


# 計算支撐 / 壓力
def get_support_resistance():
    try:
        url = (
            "https://query1.finance.yahoo.com/v8/finance/chart/"
            + stock_symbol
            + "?range=3mo&interval=1d"
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        result = data["chart"]["result"][0]

        closes = result["indicators"]["quote"][0]["close"]

        closes = [c for c in closes if c is not None]

        if len(closes) < 20:
            return None, None

        closes = closes[-60:]

        support = round(min(closes[-20:]), 2)
        resistance = round(max(closes), 2)

        return support, resistance

    except Exception as e:
        print("SR Error:", e)
        return None, None


@app.route("/")
def home():

    price = get_stock_price()

    if price is None:
        return jsonify({
            "error": "無法取得股價"
        })

    support, resistance = get_support_resistance()

    if support is None:
        suggestion = "資料不足"
    elif price > resistance:
        suggestion = "突破壓力"
    elif price < support:
        suggestion = "跌破支撐"
    else:
        suggestion = "區間內"

    data = {
        "stock": "2330",
        "name": stock_name,
        "price": price,
        "support": support,
        "resistance": resistance,
        "suggestion": suggestion,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }

    return jsonify(data)
