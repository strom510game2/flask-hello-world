
from flask import Flask, jsonify
import requests
import datetime

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
