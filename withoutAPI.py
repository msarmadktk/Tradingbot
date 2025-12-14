import os
import time
from flask import Flask, request, jsonify
import ccxt
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Set this to TRUE to test without keys.
# Set this to FALSE later when you have your keys ready.
SIMULATION_MODE = True 

# Load keys (even if empty, the bot won't crash in Simulation Mode)
load_dotenv()
API_KEY = os.getenv('BYBIT_API_KEY')
SECRET_KEY = os.getenv('BYBIT_SECRET_KEY')

app = Flask(__name__)

# --- EXCHANGE SETUP ---
exchange = None
if not SIMULATION_MODE:
    # Only connect if we are NOT in simulation mode
    if not API_KEY or not SECRET_KEY:
        print("❌ ERROR: Real keys missing! Switch SIMULATION_MODE to True or add keys.")
        exit()
        
    exchange = ccxt.bybit({
        'apiKey': API_KEY,
        'secret': SECRET_KEY,
        'enableRateLimit': True,
        'options': {'defaultType': 'linear'}
    })
    exchange.set_sandbox_mode(True)
else:
    print("⚠️  RUNNING IN SIMULATION MODE: No real trades will be placed.")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # --- 1. PARSE DATA ---
        data = request.json
        print(f"\n🔔 ALERT RECEIVED: {data}")
        
        # Clean up the symbol name
        raw_symbol = data.get('symbol', 'BTCUSDT')
        symbol = raw_symbol.replace('USDT', '/USDT') if 'USDT' in raw_symbol else raw_symbol
        action = data.get('action', 'buy')
        
        # --- 2. EXECUTION LOGIC ---
        if SIMULATION_MODE:
            # --- FAKE TRADE (FOR TESTING) ---
            print(f"🕵️  SIMULATION: Pretending to {action.upper()} {symbol}...")
            time.sleep(0.5) # Fake network delay
            print(f"✅ SIMULATION: Order 'filled' successfully!")
            
            # Return a fake order ID
            return jsonify({"status": "simulated_success", "order_id": "mock_12345"}), 200
            
        else:
            # --- REAL TRADE (FOR LATER) ---
            amount = 0.001
            if action.lower() == 'buy':
                order = exchange.create_market_buy_order(symbol, amount)
            elif action.lower() == 'sell':
                order = exchange.create_market_sell_order(symbol, amount)
            
            print(f"✅ REAL TRADE EXECUTED: ID {order['id']}")
            return jsonify({"status": "success", "order_id": order['id']}), 200

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("🤖 Bot is listening on Port 5000...")
    app.run(port=5000)