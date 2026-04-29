from flask import Flask, jsonify
import requests
import datetime

app = Flask(__name__)

# 配置資訊
STOCK_SYMBOL = "2330.TW"
STOCK_NAME = "台積電"
# 模擬瀏覽器標頭，避免被 Yahoo 封鎖
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_stock_data(range_str="1d", interval="1d"):
    """通用抓取 Yahoo Finance API 的函式"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{STOCK_SYMBOL}?range={range_str}&interval={interval}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # 檢查 HTTP 狀態碼
        return response.json()
    except Exception as e:
        print(f"API Error ({range_str}):", e)
        return None

def get_current_price():
    data = get_stock_data(range_str="1d", interval="1m")
    if data and "chart" in data:
        result = data["chart"]["result"][0]
        return float(result["meta"]["regularMarketPrice"])
    return None

def get_support_resistance():
    data = get_stock_data(range_str="3mo", interval="1d")
    if not data or "chart" not in data:
        return None, None

    try:
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        # 過濾掉 None 值
        valid_closes = [c for c in closes if c is not None]

        if len(valid_closes) < 20:
            return None, None

        # 計算邏輯：
        # 壓力位：過去 60 日最高點
        # 支撐位：過去 20 日最低點
        recent_60 = valid_closes[-60:]
        recent_20 = valid_closes[-20:]
        
        support = round(min(recent_20), 2)
        resistance = round(max(recent_60), 2)
        return support, resistance
    except (KeyError, IndexError, ValueError):
        return None, None

@app.route("/")
def home():
    price = get_current_price()
    
    if price is None:
        return jsonify({"error": "無法取得即時股價"}), 500

    support, resistance = get_support_resistance()

    # 判斷邏輯
    if support is None:
        suggestion = "數據分析不足"
    elif price >= resistance:
        suggestion = "向上突破壓力位"
    elif price <= support:
        suggestion = "跌破支撐位"
    else:
        suggestion = "區間盤整"

    return jsonify({
        "stock": STOCK_SYMBOL.split('.')[0],
        "name": STOCK_NAME,
        "current_price": price,
        "support": support,
        "resistance": resistance,
        "suggestion": suggestion,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
