from flask import Flask, jsonify
import requests
import datetime

app = Flask(__name__)

# 模擬瀏覽器標頭
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_stock_info(symbol):
    """
    取得股票名稱與即時價格
    Yahoo Finance API 台灣股票需補上 .TW (上市) 或 .TWO (上櫃)
    這裡簡單處理：若無後綴則預設補上 .TW
    """
    if "." not in symbol:
        formatted_symbol = f"{symbol}.TW"
    else:
        formatted_symbol = symbol

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{formatted_symbol}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        result = data["chart"]["result"][0]
        price = result["meta"]["regularMarketPrice"]
        # 嘗試取得股票名稱（Yahoo API 中可能存在的欄位）
        short_name = result["meta"].get("symbol", symbol) 
        
        return formatted_symbol, short_name, float(price)
    except Exception as e:
        print(f"Price Error for {symbol}:", e)
        return None, None, None

def get_support_resistance(symbol):
    """計算支撐與壓力位"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3mo&interval=1d"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        valid_closes = [c for c in closes if c is not None]

        if len(valid_closes) < 20:
            return None, None

        # 取最近 60 日資料計算
        closes_60 = valid_closes[-60:]
        support = round(min(closes_60[-20:]), 2)  # 近20日最低點
        resistance = round(max(closes_60), 2)     # 近60日最高點

        return support, resistance
    except:
        return None, None

# 使用動態路由 <stock_id>
@app.route("/stock/<stock_id>")
def check_stock(stock_id):
    # 1. 取得價格與格式化後的股號
    formatted_symbol, name, price = get_stock_info(stock_id)

    if price is None:
        return jsonify({
            "error": f"無法取得股號 {stock_id} 的資料，請確認輸入是否正確（例如：2330）。"
        }), 404

    # 2. 取得支撐壓力
    support, resistance = get_support_resistance(formatted_symbol)

    # 3. 判斷建議
    if support is None:
        suggestion = "歷史資料不足"
    elif price >= resistance:
        suggestion = "向上突破壓力位"
    elif price <= support:
        suggestion = "跌破支撐位"
    else:
        suggestion = "區間震盪"

    # 4. 回傳結果
    return jsonify({
        "stock_id": formatted_symbol,
        "name": name,
        "price": price,
        "support": support,
        "resistance": resistance,
        "suggestion": suggestion,
        "query_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/")
def index():
    return "<h1>股票查詢系統</h1><p>請在網址後方輸入股號，例如：<code>/stock/2330</code></p>"

if __name__ == "__main__":
    app.run(debug=True)
