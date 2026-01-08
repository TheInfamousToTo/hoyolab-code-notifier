#!/usr/bin/env python3
"""
HoYoLab Code Notifier
Fetches new redemption codes and sends Discord webhook notifications
"""

import json
import os
import time
import threading
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Paths
CONFIG_PATH = os.environ.get('CONFIG_PATH', '/app/data/config.json')
CODES_PATH = os.environ.get('CODES_PATH', '/app/data/sent_codes.json')

# Static game data (not user configurable)
GAMES_DATA = {
    "genshin": {
        "name": "Genshin Impact",
        "api_url": "https://api.ennead.cc/mihoyo/genshin/codes",
        "redeem_url": "https://genshin.hoyoverse.com/en/gift?code="
    },
    "starrail": {
        "name": "Honkai: Star Rail",
        "api_url": "https://api.ennead.cc/mihoyo/starrail/codes",
        "redeem_url": "https://hsr.hoyoverse.com/gift?code="
    },
    "zenless": {
        "name": "Zenless Zone Zero",
        "api_url": "https://api.ennead.cc/mihoyo/zenless/codes",
        "redeem_url": "https://zenless.hoyoverse.com/redemption?code="
    }
}

# Default configuration (user settings only)
DEFAULT_CONFIG = {
    "webhook_url": "",
    "check_interval": 300,  # 5 minutes
    "games": {
        "genshin": True,
        "starrail": True,
        "zenless": True
    }
}

# Global state
config = {}
sent_codes = {}
checker_thread = None
stop_checker = threading.Event()


def ensure_data_dir():
    """Ensure data directory exists"""
    data_dir = os.path.dirname(CONFIG_PATH)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)


def load_config():
    """Load configuration from file"""
    global config
    ensure_data_dir()
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                    elif key == "games":
                        for game_key in DEFAULT_CONFIG["games"]:
                            if game_key not in config["games"]:
                                config["games"][game_key] = True
        except Exception as e:
            print(f"Error loading config: {e}")
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()
        save_config()
    
    return config


def save_config():
    """Save configuration to file"""
    ensure_data_dir()
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def load_sent_codes():
    """Load sent codes from file"""
    global sent_codes
    ensure_data_dir()
    
    if os.path.exists(CODES_PATH):
        try:
            with open(CODES_PATH, 'r') as f:
                sent_codes = json.load(f)
        except Exception as e:
            print(f"Error loading sent codes: {e}")
            sent_codes = {"genshin": [], "starrail": [], "zenless": []}
    else:
        sent_codes = {"genshin": [], "starrail": [], "zenless": []}
        save_sent_codes()
    
    return sent_codes


def save_sent_codes():
    """Save sent codes to file"""
    ensure_data_dir()
    with open(CODES_PATH, 'w') as f:
        json.dump(sent_codes, f, indent=2)


def fetch_codes(game_key):
    """Fetch codes from API for a specific game"""
    game_data = GAMES_DATA.get(game_key, {})
    api_url = game_data.get("api_url")
    
    if not api_url:
        return []
    
    try:
        response = requests.get(api_url, headers={
            "User-Agent": "HoyoLabCodeNotifier/1.0"
        }, timeout=10)
        
        if response.status_code != 200:
            print(f"API returned {response.status_code} for {game_key}")
            return []
        
        data = response.json()
        codes = data.get("active", [])
        
        if not isinstance(codes, list):
            print(f"Invalid data format for {game_key}")
            return []
        
        return codes
    except Exception as e:
        print(f"Error fetching codes for {game_key}: {e}")
        return []


def send_discord_notification(game_key, code_data):
    """Send Discord webhook notification"""
    webhook_url = config.get("webhook_url", "")
    
    if not webhook_url:
        print("No webhook URL configured")
        return False
    
    game_data = GAMES_DATA.get(game_key, {})
    game_name = game_data.get("name", game_key)
    redeem_url = game_data.get("redeem_url", "")
    code = code_data.get("code", "")
    rewards = code_data.get("rewards", [])
    
    # Build reward string
    reward_str = ""
    if rewards:
        reward_items = []
        for reward in rewards:
            if isinstance(reward, dict):
                name = reward.get("name", "Unknown")
                count = reward.get("count", 1)
                reward_items.append(f"{name} x{count}")
            else:
                reward_items.append(str(reward))
        reward_str = "\n**Rewards:** " + ", ".join(reward_items)
    
    # Create embed for Discord
    embed = {
        "title": f"🎁 New Code Available for {game_name}!",
        "description": f"**Code:** `{code}`{reward_str}\n\n**Redeem Link:**\n{redeem_url}{code}",
        "color": get_game_color(game_key),
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "HoYoLab Code Notifier"
        }
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            print(f"Notification sent for {game_name}: {code}")
            return True
        else:
            print(f"Failed to send webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return False


def get_game_color(game_key):
    """Get embed color for each game"""
    colors = {
        "genshin": 0x00BFFF,    # Light blue
        "starrail": 0x9B59B6,   # Purple
        "zenless": 0xF1C40F     # Yellow
    }
    return colors.get(game_key, 0x7289DA)


def check_and_notify():
    """Check for new codes and send notifications"""
    global sent_codes
    
    print(f"[{datetime.now()}] Checking for new codes...")
    
    for game_key in GAMES_DATA:
        if not config["games"].get(game_key, False):
            continue
        
        codes = fetch_codes(game_key)
        game_sent = sent_codes.get(game_key, [])
        
        for code_data in codes:
            code = code_data.get("code", "").upper()
            
            if code and code not in game_sent:
                print(f"New code found for {game_key}: {code}")
                
                if send_discord_notification(game_key, code_data):
                    if game_key not in sent_codes:
                        sent_codes[game_key] = []
                    sent_codes[game_key].append(code)
                    save_sent_codes()
                
                # Rate limit: wait between notifications
                time.sleep(2)


def checker_loop():
    """Background thread for periodic code checking"""
    while not stop_checker.is_set():
        try:
            check_and_notify()
        except Exception as e:
            print(f"Error in checker loop: {e}")
        
        interval = config.get("check_interval", 300)
        stop_checker.wait(interval)


def start_checker():
    """Start the background checker thread"""
    global checker_thread, stop_checker
    
    stop_checker.clear()
    checker_thread = threading.Thread(target=checker_loop, daemon=True)
    checker_thread.start()
    print("Code checker started")


# Flask Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    # Combine static game data with user config for GUI
    games_combined = {}
    for game_key, game_data in GAMES_DATA.items():
        games_combined[game_key] = {
            "name": game_data["name"],
            "enabled": config["games"].get(game_key, False)
        }
    
    return jsonify({
        "webhook_url": config.get("webhook_url", ""),
        "check_interval": config.get("check_interval", 300),
        "games": games_combined
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global config
    
    data = request.json
    
    if "webhook_url" in data:
        config["webhook_url"] = data["webhook_url"]
    
    if "check_interval" in data:
        config["check_interval"] = max(60, int(data["check_interval"]))
    
    if "games" in data:
        for game_key, game_data in data["games"].items():
            if game_key in GAMES_DATA:
                if isinstance(game_data, bool):
                    config["games"][game_key] = game_data
                elif "enabled" in game_data:
                    config["games"][game_key] = bool(game_data["enabled"])
    
    save_config()
    return jsonify({"success": True, "message": "Configuration saved"})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    return jsonify({
        "sent_codes": sent_codes,
        "checker_running": checker_thread is not None and checker_thread.is_alive(),
        "last_check": datetime.now().isoformat()
    })


@app.route('/api/check-now', methods=['POST'])
def check_now():
    """Manually trigger a code check"""
    threading.Thread(target=check_and_notify, daemon=True).start()
    return jsonify({"success": True, "message": "Check triggered"})


@app.route('/api/test-webhook', methods=['POST'])
def test_webhook():
    """Test webhook configuration"""
    webhook_url = config.get("webhook_url", "")
    
    if not webhook_url:
        return jsonify({"success": False, "message": "No webhook URL configured"})
    
    payload = {
        "embeds": [{
            "title": "🔔 Test Notification",
            "description": "HoYoLab Code Notifier is configured correctly!",
            "color": 0x2ECC71,
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            return jsonify({"success": True, "message": "Test notification sent"})
        else:
            return jsonify({"success": False, "message": f"Webhook returned {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/api/clear-codes', methods=['POST'])
def clear_codes():
    """Clear sent codes history"""
    global sent_codes
    
    data = request.json
    game = data.get("game")
    
    if game and game in sent_codes:
        sent_codes[game] = []
    else:
        sent_codes = {"genshin": [], "starrail": [], "zenless": []}
    
    save_sent_codes()
    return jsonify({"success": True, "message": "Codes cleared"})


if __name__ == '__main__':
    print("Starting HoYoLab Code Notifier...")
    
    # Load configuration and sent codes
    load_config()
    load_sent_codes()
    
    # Start background checker
    start_checker()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
