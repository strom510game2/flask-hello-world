
from flask import Flask, jsonify
import requests
import datetime

from flask import Flask, jsonify
import random
import datetime

app = Flask(__name__)

# 自選股
stocks = {
    "2330": "台積電",
    "2409": "友達",
    "3481": "群創"
}

def calc_levels(price):
    support = round(price * 0.97, 2)
    resistance = round(price * 1.03, 2)

    if price > resistance:
        suggestion = "突破壓力，偏多"
    elif price < support:
        suggestion = "跌破支撐，觀察"
    else:
        suggestion = "區間震盪"

    return support, resistance, suggestion

@app.route("/")
def home():
    data = []

    for code, name in stocks.items():
        price = round(random.uniform(10, 1000), 2)
        support, resistance, suggestion = calc_levels(price)

        data.append({
            "stock": code,
            "name": name,
            "price": price,
            "support": support,
            "resistance": resistance,
            "suggestion": suggestion,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        })

    return jsonify(data)

app = Flask(__name__)

def get_stock_price(stock_no):
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_no}.tw"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if data["msgArray"]:
            price = float(data["msgArray"][0]["z"])
            return price

        return None

    except Exception as e:
        print("Error:", e)
        return None
