import yfinance as yf
import json
from datetime import datetime
import pytz

symbols = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Platinum": "PL=F",
    "Palladium": "PA=F",
    "USDILS": "USDILS=X"
}

translations = {
    "Gold": "זהב",
    "Silver": "כסף",
    "Platinum": "פלטינה",
    "Palladium": "פלדיום",
    "USDILS": "דולר/שקל",
    "Gold_Silver_Ratio": "יחס זהב/כסף"
}

def get_price_robust(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    try:
        price = ticker.fast_info.last_price
        if price is not None and price > 0:
            return price, ticker.fast_info.previous_close
    except:
        pass
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
    prev_closes_raw = {} # הוספנו מילון לשמירת מחירי הסגירה הקודמים
    
    # הגדרת שעון ישראל
    israel_tz = pytz.timezone('Asia/Jerusalem')
    now_israel = datetime.now(pytz.utc).astimezone(israel_tz)
    timestamp = now_israel.strftime("%Y-%m-%d %H:%M:%S")
    time_only = now_israel.strftime("%H:%M:%S")

    html_rows = ""

    for name, ticker in symbols.items():
        price, prev_close = get_price_robust(ticker)
        
        if price:
            change = 0
            if prev_close:
                change = ((price - prev_close) / prev_close) * 100
            
            rounded_price = round(price, 4) if name == "USDILS" else round(price, 2)
            rounded_change = round(change, 2)
            
            results[name] = {
                "price": rounded_price,
                "change": rounded_change,
                "updated_at": timestamp
            }
            prices_raw[name] = price
            prev_closes_raw[name] = prev_close # שמירת מחיר הסגירה הקודם
            
            # יצירת שורה לטבלה
            name_he = translations.get(name, name)
            price_str = f"₪{rounded_price:.4f}" if name == "USDILS" else f"${rounded_price:,.2f}"
            
            if rounded_change > 0:
                change_html = f'<span style="color: #28a745; font-weight: bold; direction: ltr; display: inline-block;">+{rounded_change}%</span>'
            elif rounded_change < 0:
                change_html = f'<span style="color: #dc3545; font-weight: bold; direction: ltr; display: inline-block;">{rounded_change}%</span>'
            else:
                change_html = f'<span style="color: #6c757d; font-weight: bold; direction: ltr; display: inline-block;">-</span>'

            html_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{name_he}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; direction: ltr;">{price_str}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{change_html}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; font-size: 0.85em; color: #888;">{time_only}</td>
            </tr>
            """

    # --- הוספת חישוב יחס זהב/כסף והשינוי היומי שלו ---
    if "Gold" in prices_raw and "Silver" in prices_raw:
        current_ratio = prices_raw["Gold"] / prices_raw["Silver"]
        
        prev_gold = prev_closes_raw.get("Gold")
        prev_silver = prev_closes_raw.get("Silver")
        
        ratio_change = 0
        if prev_gold and prev_silver:
            prev_ratio = prev_gold / prev_silver
            ratio_change = ((current_ratio - prev_ratio) / prev_ratio) * 100
            
        rounded_ratio = round(current_ratio, 2)
        rounded_ratio_change = round(ratio_change, 2)
        
        results["Gold_Silver_Ratio"] = {
            "price": rounded_ratio,
            "change": rounded_ratio_change,
            "updated_at": timestamp
        }
        
        if rounded_ratio_change > 0:
            ratio_change_html = f'<span style="color: #28a745; font-weight: bold; direction: ltr; display: inline-block;">+{rounded_ratio_change}%</span>'
        elif rounded_ratio_change < 0:
            ratio_change_html = f'<span style="color: #dc3545; font-weight: bold; direction: ltr; display: inline-block;">{rounded_ratio_change}%</span>'
        else:
            ratio_change_html = f'<span style="color: #6c757d; font-weight: bold; direction: ltr; display: inline-block;">-</span>'

        html_rows += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #eee;">{translations['Gold_Silver_Ratio']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; direction: ltr;">{rounded_ratio}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee;">{ratio_change_html}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; font-size: 0.85em; color: #888;">{time_only}</td>
        </tr>
        """

    with open("prices.json", "w") as f:
        json.dump(results, f, indent=4)

    html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; background: transparent; }}
        .coinfolio-widget {{ width: 100%; max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 20px; box-sizing: border-box; }}
        .coinfolio-table {{ width: 100%; border-collapse: collapse; text-align: right; }}
        .coinfolio-table th {{ color: #555; font-weight: bold; padding: 12px; border-bottom: 1px solid #eee; }}
    </style>
    <script>
        setTimeout(function() {{ location.reload(); }}, 300000);
    </script>
</head>
<body>
    <div class="coinfolio-widget">
        <h3 style="margin-top: 0;">מחירי חוזים עתידיים בזמן אמת</h3>
        <table class="coinfolio-table">
            <thead>
                <tr>
                    <th>נכס</th>
                    <th>מחיר (USD)</th>
                    <th>שינוי יומי</th>
                    <th>עדכון אחרון</th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    get_data()
