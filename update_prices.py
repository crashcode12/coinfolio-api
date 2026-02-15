import yfinance as yf
import json
import csv
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# הגדרות בסיסיות
israel_tz = pytz.timezone('Asia/Jerusalem')
now_israel = datetime.now(pytz.utc).astimezone(israel_tz)
timestamp = now_israel.strftime("%Y-%m-%d %H:%M:%S")

symbols_yf = {"Gold": "GC=F", "Silver": "SI=F", "Platinum": "PL=F", "Palladium": "PA=F", "USDILS": "USDILS=X"}
translations = {"Gold": "זהב", "Silver": "כסף", "Platinum": "פלטינה", "Palladium": "פלדיום", "USDILS": "דולר/שקל", "Gold_Silver_Ratio": "יחס זהב/כסף"}

def get_metalcharts_prices():
    """ניסיון למשוך מחירי ספוט מ-MetalCharts"""
    prices = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        # סריקת זהב וכסף (האתר מציג אותם בדף הראשי)
        response = requests.get("https://metalcharts.org/", headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # כאן מתבצע חיפוש המחיר לפי מבנה האתר (מבוסס על התמונות ששלחת)
        # הערה: סריקה כזו רגישה לשינויי עיצוב באתר
        return None # נחזיר None כרגע כדי להפעיל את הגיבוי עד שנוודא יציבות סריקה
    except:
        return None

def get_price_yf(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    try:
        price = ticker.fast_info.last_price
        return price, ticker.fast_info.previous_close
    except:
        return None, None

def update():
    results = {}
    prices_raw = {}
    
    # 1. ניסיון משיכה מ-MetalCharts (כרגע מוגדר לדלג לגיבוי עד הטמעה סופית של הסורק)
    mc_prices = get_metalcharts_prices()
    
    # 2. איסוף נתונים (עם גיבוי ליאהו)
    for name, ticker in symbols_yf.items():
        price, prev_close = get_price_yf(ticker) # גיבוי יאהו
        if price:
            change = ((price - prev_close) / prev_close) * 100 if prev_close else 0
            results[name] = {"price": round(price, 4 if name=="USDILS" else 2), "change": round(change, 2), "updated_at": timestamp}
            prices_raw[name] = price

    # 3. חישוב יחס זהב/כסף
    if "Gold" in prices_raw and "Silver" in prices_raw:
        ratio = prices_raw["Gold"] / prices_raw["Silver"]
        results["Gold_Silver_Ratio"] = {"price": round(ratio, 2), "updated_at": timestamp}

    # 4. שמירת JSON (לשימוש מיידי באתר)
    with open("prices.json", "w") as f:
        json.dump(results, f, indent=4)

    # 5. עדכון בסיס נתונים היסטורי (CSV)
    file_exists = os.path.isfile("price_history.csv")
    with open("price_history.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Asset", "Price", "Change"])
        for name, data in results.items():
            writer.writerow([timestamp, name, data['price'], data.get('change', 0)])

    # 6. יצירת HTML (כמו שעשינו קודם)
    # ... (השמטתי כאן את קוד ה-HTML כדי לקצר, הוא נשאר זהה למה שיש לך)
    print(f"Update finished at {timestamp}")

if __name__ == "__main__":
    update()
