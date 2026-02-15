import yfinance as yf
import json
from datetime import datetime

# חזרנו לסימולי החוזים העתידיים (הכי יציב ביאהו) + שער השקל
symbols = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",
    "Palladium": "PA=F",
    "USDILS": "USDILS=X"
}

def get_price_robust(ticker_symbol):
    """מנגנון חכם: מנסה קודם למשוך מחיר חי, ואם הבורסה סגורה מביא מחיר אחרון"""
    ticker = yf.Ticker(ticker_symbol)
    
    # ניסיון 1: מחיר חי (Fast Info)
    try:
        price = ticker.fast_info.last_price
        if price is not None and price > 0:
            return price, ticker.fast_info.previous_close
    except:
        pass

    # ניסיון 2: חפירה בהיסטוריה של הימים האחרונים
    try:
        hist = ticker.history(period="5d")
        if not hist.empty:
            return hist['Close'].iloc[-1], hist['Open'].iloc[-1]
    except:
        pass
        
    return None, None

def get_data():
    results = {}
    prices_raw = {} 

    for name, ticker in symbols.items():
        print(f"Fetching {name} ({ticker})...")
        price, prev_close = get_price_robust(ticker)
        
        if price:
            change = 0
            if prev_close:
                change = ((price - prev_close) / prev_close) * 100
            
            results[name] = {
                "price": round(price, 4 if name == "USDILS" else 2),
                "change": round(change, 2),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            prices_raw[name] = price
            print(f"Success: {name} is {price}")
        else:
            print(f"Warning: Could not fetch price for {name}")

    # חישוב יחס זהב/כסף
    if "Gold" in prices_raw and "Silver" in prices_raw:
        ratio = prices_raw["Gold"] / prices_raw["Silver"]
        results["Gold_Silver_Ratio"] = {
            "price": round(ratio, 2),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    with open("prices.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Update complete.")

if __name__ == "__main__":
    get_data()
