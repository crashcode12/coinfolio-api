import yfinance as yf
import json
from datetime import datetime

# סימולי ספוט (Spot) מול הדולר ושער חליפין
symbols = {
    "Gold": "XAUUSD=X",
    "Silver": "XAGUSD=X",
    "Platinum": "XPTUSD=X",
    "Palladium": "XPDUSD=X",
    "USDILS": "USDILS=X"
}

def get_data():
    results = {}
    prices_raw = {} 

    for name, ticker in symbols.items():
        try:
            data = yf.Ticker(ticker)
            info = data.fast_info
            
            last_price = info.last_price
            prev_close = info.previous_close
            
            # חישוב שינוי יומי באחוזים
            change = ((last_price - prev_close) / prev_close) * 100
            
            results[name] = {
                "price": round(last_price, 4 if name == "USDILS" else 2),
                "change": round(change, 2),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            prices_raw[name] = last_price
            
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    # חישוב יחס זהב/כסף (XAU/XAG)
    if "Gold" in prices_raw and "Silver" in prices_raw:
        ratio = prices_raw["Gold"] / prices_raw["Silver"]
        results["Gold_Silver_Ratio"] = {
            "price": round(ratio, 2),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # שמירה לקובץ JSON
    with open("prices.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Prices updated successfully.")

if __name__ == "__main__":
    get_data()
