from flask import Flask, render_template, jsonify
import requests
import datetime

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_stock_data(symbol):
    if "." not in symbol:
        symbol = f"{symbol}.TW"
    try:
        # 同時抓取價格與歷史資料
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3mo&interval=1d"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()["chart"]["result"][0]
        
        price = data["meta"]["regularMarketPrice"]
        prev_close = data["meta"]["previousClose"]
        change = round(price - prev_close, 2)
        change_percent = round((change / prev_close) * 100, 2)
        
        closes = [c for c in data["indicators"]["quote"][0]["close"] if c is not None]
        support = round(min(closes[-20:]), 2)
        resistance = round(max(closes[-60:]), 2)

        return {
            "symbol": symbol.split('.')[0],
            "price": price,
            "change": change,
            "change_percent": change_percent,
            "support": support,
            "resistance": resistance,
            "status": "突破" if price >= resistance else "超跌" if price <= support else "震盪"
        }
    except:
        return None

@app.route('/')
def index():
    # 預設顯示幾支股票
    default_stocks = ["2330", "2317", "2454"]
    stocks_info = []
    for s in default_stocks:
        data = get_stock_data(s)
        if data: stocks_info.append(data)
    
    return render_template('index.html', stocks=stocks_info)

if __name__ == "__main__":
    app.run(debug=True)
