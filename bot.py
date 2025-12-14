import os
import time
from flask import Flask, request, jsonify
import ccxt
from dotenv import load_dotenv

# --- 1. LOAD SECRETS ---
# This finds the .env file and loads the variables
load_dotenv()

# We get the keys safely from the environment
API_KEY = os.getenv('BYBIT_API_KEY')
SECRET_KEY = os.getenv('BYBIT_SECRET_KEY')

# Safety Check: Stop the bot immediately if keys are missing
if not API_KEY or not SECRET_KEY:
    print("❌ ERROR: Keys not found! Make sure you created the .env file.")
    exit()

app = Flask(__name__)

# --- 2. BYBIT TESTNET CONFIGURATION ---
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'linear',  # USDT Perpetuals
    }
})

# CRITICAL SAFETY LOCK: Forces Testnet
exchange.set_sandbox_mode(True)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # --- 3. PARSE DATA ---
        data = request.json
        print(f"🔔 ALERT RECEIVED: {data}")
        
        raw_symbol = data.get('symbol', 'BTCUSDT')
        action = data.get('action', 'buy')
        
        # Format Symbol (BTCUSDT -> BTC/USDT)
        symbol = raw_symbol
        if 'USDT' in symbol and '/' not in symbol:
            symbol = symbol.replace('USDT', '/USDT')
        
        # --- 4. EXECUTE TRADE ---
        amount = 0.001 
        
        order = None
        if action.lower() == 'buy':
            print(f"🚀 BUYING: {symbol}")
            order = exchange.create_market_buy_order(symbol, amount)
            print(f"✅ SUCCESS: {order['id']}")
            
        elif action.lower() == 'sell':
            print(f"🔻 SELLING: {symbol}")
            order = exchange.create_market_sell_order(symbol, amount)
            print(f"✅ SUCCESS: {order['id']}")
            
        else:
            return jsonify({"status": "ignored"}), 400

        return jsonify({"status": "success", "order_id": order['id']}), 200

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🤖 Bot is active. Keys loaded safely.")
    app.run(port=5000)