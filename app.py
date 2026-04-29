from flask import Flask, jsonify
import requests
import datetime

app = Flask(__name__)

# 固定股票：台積電
stock_no = "2330"
stock_name = "台積電"


# 取得股價（最新收盤價）
def get_stock_price():
    try:
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={stock_no}"

        response = requests.get(url, timeout=10)
        data = response.json()

        closes = []

        for row in data["data"]:
            close_price = row[6].replace(",", "")
            closes.append(float(close_price))

        if len(closes) == 0:
            return None

        return closes[-1]

    except Exception as e:
        print("Price Error:", e)
        return None


# 計算真支撐 / 壓力
def get_support_resistance():
    try:
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={stock_no}"

        response = requests.get(url, timeout=10)
        data = response.json()

        closes = []

        for row in data["data"]:
            close_price = row[6].replace(",", "")
            closes.append(float(close_price))

        closes = closes[-60:]

        if len(closes) < 20:
            return None, None

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
        return jsonify({"error": "無法取得股價"})

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
        "stock": stock_no,
        "name": stock_name,
        "price": price,
        "support": support,
        "resistance": resistance,
        "suggestion": suggestion,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }

    return jsonify(data)
