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
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dateutil.tz import tzutc
import pytz

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
    "webhooks": [],  # List of webhook configs: [{name, url, games: {genshin: true, ...}}]
    "check_interval": 300,  # 5 minutes
    "timezone": "UTC",  # Timezone for displaying expiration times (e.g., "Europe/Paris", "America/New_York", "Asia/Tokyo")
}

# Global state
config = {}
sent_codes = {}
code_expiration_data = {}  # Store expiration dates for codes
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
                
                # Migrate old config format to new format
                if "webhook_url" in config and config["webhook_url"]:
                    # Old format had single webhook_url, migrate it
                    old_url = config["webhook_url"]
                    old_games = config.get("games", {"genshin": True, "starrail": True, "zenless": True})
                    if not config.get("webhooks") or not isinstance(config["webhooks"], list):
                        config["webhooks"] = [{
                            "name": "Main Webhook",
                            "url": old_url,
                            "games": old_games
                        }]
                    del config["webhook_url"]
                    if "games" in config:
                        del config["games"]
                    save_config()
                
                # Ensure webhooks is a list
                if not isinstance(config.get("webhooks"), list):
                    config["webhooks"] = []
                    
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
    global sent_codes, code_expiration_data
    ensure_data_dir()
    
    if os.path.exists(CODES_PATH):
        try:
            with open(CODES_PATH, 'r') as f:
                data = json.load(f)
                # Support both old format (just codes) and new format (with expiration)
                if isinstance(data, dict):
                    # Check if it's new format with expiration data
                    if "codes" in data and "expiration" in data:
                        sent_codes = data["codes"]
                        code_expiration_data = data["expiration"]
                    else:
                        # Old format - just game: [codes] structure
                        sent_codes = data
                        code_expiration_data = {"genshin": {}, "starrail": {}, "zenless": {}}
                else:
                    sent_codes = {"genshin": [], "starrail": [], "zenless": []}
                    code_expiration_data = {"genshin": {}, "starrail": {}, "zenless": {}}
        except Exception as e:
            print(f"Error loading sent codes: {e}")
            sent_codes = {"genshin": [], "starrail": [], "zenless": []}
            code_expiration_data = {"genshin": {}, "starrail": {}, "zenless": {}}
    else:
        sent_codes = {"genshin": [], "starrail": [], "zenless": []}
        code_expiration_data = {"genshin": {}, "starrail": {}, "zenless": {}}
        save_sent_codes()
    
    return sent_codes


def save_sent_codes():
    """Save sent codes to file"""
    ensure_data_dir()
    data = {
        "codes": sent_codes,
        "expiration": code_expiration_data
    }
    with open(CODES_PATH, 'w') as f:
        json.dump(data, f, indent=2)


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


def parse_expiration_date(code_data):
    """Parse expiration date from code data"""
    # Try different possible field names for expiration
    expiration_fields = ["expiration", "expires", "expire_date", "expiry", "valid_until", "end_date"]
    
    for field in expiration_fields:
        if field in code_data and code_data[field]:
            try:
                exp_value = code_data[field]
                if isinstance(exp_value, str):
                    return date_parser.parse(exp_value)
                elif isinstance(exp_value, (int, float)):
                    # Unix timestamp
                    return datetime.fromtimestamp(exp_value, tz=tzutc())
            except:
                continue
    return None


def get_expiration_status(expiration_date):
    """Get expiration status and urgency level"""
    if not expiration_date:
        return {"status": "unknown", "urgency": "normal", "text": "No expiration info"}
    
    now = datetime.now(tzutc()) if expiration_date.tzinfo else datetime.now()
    time_left = expiration_date - now
    
    if time_left.total_seconds() <= 0:
        return {"status": "expired", "urgency": "expired", "text": "Expired"}
    
    hours_left = time_left.total_seconds() / 3600
    
    # Less than 48 hours = critical (red)
    if hours_left <= 48:
        if hours_left < 1:
            mins = int(time_left.total_seconds() / 60)
            return {"status": "expiring", "urgency": "critical", "text": f"Expires in {mins}m"}
        return {"status": "expiring", "urgency": "critical", "text": f"Expires in {int(hours_left)}h"}
    elif hours_left <= 72:
        return {"status": "active", "urgency": "soon", "text": f"Expires in {int(hours_left)}h"}
    else:
        days_left = int(time_left.days)
        return {"status": "active", "urgency": "normal", "text": f"Expires in {days_left}d"}


def get_user_timezone():
    """Get the configured timezone"""
    tz_name = config.get("timezone", "UTC")
    try:
        return pytz.timezone(tz_name)
    except:
        return pytz.UTC


def format_expiration_for_discord(expiration_date):
    """Format expiration date for Discord embed with timezone-aware date/time"""
    if not expiration_date:
        return ""
    
    status = get_expiration_status(expiration_date)
    
    # Convert to user's timezone for display
    user_tz = get_user_timezone()
    if expiration_date.tzinfo is None:
        expiration_date = pytz.UTC.localize(expiration_date)
    local_exp = expiration_date.astimezone(user_tz)
    
    # Format the date/time
    formatted_time = local_exp.strftime("%b %d, %Y at %H:%M")
    tz_abbr = local_exp.strftime("%Z")
    
    # Use red for codes expiring within 48 hours
    if status["urgency"] == "critical":
        return f"\n\n🔴 **EXPIRING SOON!**\n⏰ Expires: **{formatted_time} {tz_abbr}** ({status['text']})"
    elif status["urgency"] == "expired":
        return f"\n\n⚫ **EXPIRED**"
    else:
        urgency_emoji = {
            "soon": "🟠",
            "normal": "🟢"
        }
        emoji = urgency_emoji.get(status["urgency"], "🟢")
        return f"\n\n{emoji} ⏰ Expires: **{formatted_time} {tz_abbr}**"


def send_discord_notification(game_key, code_data):
    """Send Discord webhook notification to all configured webhooks"""
    # Get all webhook URLs for this game
    webhook_urls = get_webhooks_for_game(game_key)
    
    if not webhook_urls:
        print(f"No webhook URLs configured for {game_key}")
        return False
    
    game_data = GAMES_DATA.get(game_key, {})
    game_name = game_data.get("name", game_key)
    redeem_url = game_data.get("redeem_url", "")
    code = code_data.get("code", "")
    rewards = code_data.get("rewards", [])
    
    # Parse and store expiration date
    expiration_date = parse_expiration_date(code_data)
    expiration_text = format_expiration_for_discord(expiration_date)
    
    # Store expiration data
    if expiration_date:
        if game_key not in code_expiration_data:
            code_expiration_data[game_key] = {}
        code_expiration_data[game_key][code] = expiration_date.isoformat()
    
    # Game-specific mascot names and avatars
    mascot_data = {
        "genshin": {
            "name": "Paimon",
            "avatar": "https://fastcdn.hoyoverse.com/static-resource-v2/2023/11/08/9db76fb146f82c045bc276956f86e047_6878380451593228482.png"
        },
        "starrail": {
            "name": "PomPom",
            "avatar": "https://fastcdn.hoyoverse.com/static-resource-v2/2025/09/24/de09aa694c26b87448cf03af683e3109_6737621355140099473.jpg"
        },
        "zenless": {
            "name": "Eous",
            "avatar": "https://hyl-static-res-prod.hoyolab.com/communityweb/business/nap.png"
        }
    }
    
    mascot = mascot_data.get(game_key, {"name": "HoYoLab", "avatar": ""})
    
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
        "description": f"**Code:** `{code}`{reward_str}\n\n**Redeem Link:**\n{redeem_url}{code}{expiration_text}",
        "color": get_game_color(game_key),
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "HoYoLab Code Notifier"
        }
    }
    
    payload = {
        "username": mascot["name"],
        "avatar_url": mascot["avatar"],
        "embeds": [embed]
    }
    
    # Send to all webhooks
    success_count = 0
    for webhook_url in webhook_urls:
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                print(f"Notification sent to webhook for {game_name}: {code}")
                success_count += 1
            else:
                print(f"Failed to send webhook: {response.status_code}")
        except Exception as e:
            print(f"Error sending webhook: {e}")
        
        # Rate limit between webhooks
        if len(webhook_urls) > 1:
            time.sleep(0.5)
    
    # Send to statistics backend after successful Discord notification
    if success_count > 0:
        try:
            stats_payload = {
                "game": game_key,
                "code": code,
                "rewards": reward_str.replace("\n**Rewards:** ", "") if reward_str else "",
                "expiration_date": expiration_date.isoformat() if expiration_date else None
            }
            requests.post(
                "https://hoyolab-backend.satrawi.cc/api/webhook/code-discovered",
                json=stats_payload,
                timeout=5
            )
            print(f"Code {code} sent to statistics backend")
        except Exception as e:
            print(f"Failed to send to statistics backend: {e}")
    
    return success_count > 0


def get_webhooks_for_game(game_key):
    """Get all webhook URLs that have this game enabled"""
    webhook_urls = []
    
    webhooks = config.get("webhooks", [])
    for webhook in webhooks:
        if isinstance(webhook, dict):
            url = webhook.get("url", "")
            games = webhook.get("games", {})
            # Check if this game is enabled for this webhook
            if url and games.get(game_key, False):
                webhook_urls.append(url)
    
    return webhook_urls


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
        # Check if any webhook has this game enabled
        webhook_urls = get_webhooks_for_game(game_key)
        if not webhook_urls:
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
    # Get game info for GUI
    games_info = {}
    for game_key, game_data in GAMES_DATA.items():
        games_info[game_key] = {
            "name": game_data["name"]
        }
    
    return jsonify({
        "webhooks": config.get("webhooks", []),
        "check_interval": config.get("check_interval", 300),
        "timezone": config.get("timezone", "UTC"),
        "games_info": games_info
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global config
    
    data = request.json
    
    if "check_interval" in data:
        config["check_interval"] = max(60, int(data["check_interval"]))
    
    if "timezone" in data:
        # Validate timezone
        try:
            pytz.timezone(data["timezone"])
            config["timezone"] = data["timezone"]
        except:
            pass  # Keep existing timezone if invalid
    
    if "webhooks" in data:
        config["webhooks"] = data["webhooks"]
    
    save_config()
    return jsonify({"success": True, "message": "Configuration saved"})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    # Reload sent codes from file to reflect any manual changes
    load_sent_codes()
    
    # Build codes with expiration info for the UI
    codes_with_expiration = {}
    user_tz = get_user_timezone()
    
    for game_key in GAMES_DATA:
        game_codes = sent_codes.get(game_key, [])
        game_exp = code_expiration_data.get(game_key, {})
        codes_with_expiration[game_key] = []
        
        for code in game_codes:
            code_info = {"code": code}
            if code in game_exp:
                try:
                    exp_date = date_parser.parse(game_exp[code])
                    status = get_expiration_status(exp_date)
                    
                    # Format expiration time in user's timezone
                    if exp_date.tzinfo is None:
                        exp_date = pytz.UTC.localize(exp_date)
                    local_exp = exp_date.astimezone(user_tz)
                    formatted_time = local_exp.strftime("%b %d, %Y at %H:%M %Z")
                    
                    code_info["expiration"] = game_exp[code]
                    code_info["expiration_formatted"] = formatted_time
                    code_info["expiration_status"] = status
                except:
                    code_info["expiration_status"] = {"status": "unknown", "urgency": "normal", "text": "No expiration info"}
            else:
                code_info["expiration_status"] = {"status": "unknown", "urgency": "normal", "text": "No expiration info"}
            
            codes_with_expiration[game_key].append(code_info)
    
    return jsonify({
        "sent_codes": sent_codes,
        "codes_with_expiration": codes_with_expiration,
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
    """Test all webhooks or a specific one"""
    data = request.json or {}
    webhook_url = data.get("webhook_url")
    
    if webhook_url:
        # Test a specific URL provided in the request
        webhook_urls = [webhook_url]
    else:
        # Test all configured webhooks
        webhooks = config.get("webhooks", [])
        webhook_urls = [w.get("url") for w in webhooks if w.get("url")]
    
    if not webhook_urls:
        return jsonify({"success": False, "message": "No webhook URLs configured"})
    
    payload = {
        "username": "Paimon",
        "avatar_url": "https://fastcdn.hoyoverse.com/static-resource-v2/2023/11/08/9db76fb146f82c045bc276956f86e047_6878380451593228482.png",
        "embeds": [{
            "title": "🔔 Test Notification",
            "description": "HoYoLab Code Notifier is configured correctly!",
            "color": 0x2ECC71,
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    
    success_count = 0
    errors = []
    
    for url in webhook_urls:
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                success_count += 1
            else:
                errors.append(f"Webhook returned {response.status_code}")
        except Exception as e:
            errors.append(str(e))
    
    if success_count > 0:
        msg = f"Test notification sent to {success_count} webhook(s)"
        if errors:
            msg += f" ({len(errors)} failed)"
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "message": f"All webhooks failed: {', '.join(errors[:3])}"})


@app.route('/api/webhooks', methods=['GET'])
def get_webhooks():
    """Get all webhooks"""
    return jsonify({"webhooks": config.get("webhooks", [])})


@app.route('/api/webhooks', methods=['POST'])
def add_webhook():
    """Add a new webhook"""
    data = request.json
    webhook_url = data.get("url", "").strip()
    webhook_name = data.get("name", "Webhook").strip()
    games = data.get("games", {"genshin": True, "starrail": True, "zenless": True})
    
    if not webhook_url:
        return jsonify({"success": False, "message": "Webhook URL is required"}), 400
    
    if "webhooks" not in config:
        config["webhooks"] = []
    
    # Check for duplicates
    for existing in config["webhooks"]:
        if existing.get("url") == webhook_url:
            return jsonify({"success": False, "message": "Webhook already exists"}), 400
    
    config["webhooks"].append({
        "name": webhook_name,
        "url": webhook_url,
        "games": games
    })
    save_config()
    
    return jsonify({"success": True, "message": "Webhook added"})


@app.route('/api/webhooks/<int:index>', methods=['PUT'])
def update_webhook(index):
    """Update a webhook"""
    webhooks = config.get("webhooks", [])
    
    if index < 0 or index >= len(webhooks):
        return jsonify({"success": False, "message": "Invalid webhook index"}), 400
    
    data = request.json
    
    if "name" in data:
        config["webhooks"][index]["name"] = data["name"].strip()
    if "url" in data:
        config["webhooks"][index]["url"] = data["url"].strip()
    if "games" in data:
        config["webhooks"][index]["games"] = data["games"]
    
    save_config()
    return jsonify({"success": True, "message": "Webhook updated"})


@app.route('/api/webhooks/<int:index>', methods=['DELETE'])
def remove_webhook(index):
    """Remove a webhook"""
    webhooks = config.get("webhooks", [])
    
    if index < 0 or index >= len(webhooks):
        return jsonify({"success": False, "message": "Invalid webhook index"}), 400
    
    config["webhooks"].pop(index)
    save_config()
    
    return jsonify({"success": True, "message": "Webhook removed"})


@app.route('/api/webhooks/<int:index>/test', methods=['POST'])
def test_specific_webhook(index):
    """Test a specific webhook"""
    webhooks = config.get("webhooks", [])
    
    if index < 0 or index >= len(webhooks):
        return jsonify({"success": False, "message": "Invalid webhook index"}), 400
    
    webhook = webhooks[index]
    webhook_url = webhook.get("url", "")
    webhook_name = webhook.get("name", "Webhook")
    
    payload = {
        "username": "Paimon",
        "avatar_url": "https://fastcdn.hoyoverse.com/static-resource-v2/2023/11/08/9db76fb146f82c045bc276956f86e047_6878380451593228482.png",
        "embeds": [{
            "title": f"🔔 Test Notification",
            "description": f"Webhook **{webhook_name}** is configured correctly!",
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


def get_support_payload():
    """Get the support notification payload"""
    return {
        "username": "HoYoLab Code Notifier",
        "avatar_url": "https://fastcdn.hoyoverse.com/static-resource-v2/2023/11/08/9db76fb146f82c045bc276956f86e047_6878380451593228482.png",
        "embeds": [{
            "title": "💝 Support HoYoLab Code Notifier",
            "description": (
                "Hey Travelers! 👋\n\n"
                "Enjoying automatic code notifications? This project is **free & open source**, "
                "crafted with love by **TheInfamousToTo**!\n\n"
                "If it's saved you from missing codes, consider giving back:"
            ),
            "color": 0x7C83FF,  # Purple/accent color matching the app
            "fields": [
                {
                    "name": "⭐ Star the Project",
                    "value": "[GitHub Repository](https://github.com/TheInfamousToTo/hoyolab-code-notifier)",
                    "inline": True
                },
                {
                    "name": "💖 Sponsor",
                    "value": "[GitHub Sponsors](https://github.com/sponsors/TheInfamousToTo)",
                    "inline": True
                },
                {
                    "name": "☕ Buy Me a Coffee",
                    "value": "[buymeacoffee.com](https://www.buymeacoffee.com/theinfamoustoto)",
                    "inline": True
                },
                {
                    "name": "❤️ Ko-fi",
                    "value": "[ko-fi.com](https://ko-fi.com/theinfamoustoto)",
                    "inline": True
                },
                {
                    "name": "💳 PayPal",
                    "value": "[paypal.me](https://paypal.me/alsatrawi)",
                    "inline": True
                },
                {
                    "name": "🎮 In-Game Support",
                    "value": "Genshin UID: `707631903`\n*(Genesis Crystals welcome!)*",
                    "inline": True
                }
            ],
            "thumbnail": {
                "url": "https://fastcdn.hoyoverse.com/static-resource-v2/2023/11/08/9db76fb146f82c045bc276956f86e047_6878380451593228482.png"
            },
            "footer": {
                "text": "Every bit helps keep this project alive! Thank you! 🙏",
                "icon_url": "https://github.githubassets.com/favicons/favicon.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        }]
    }


@app.route('/api/webhooks/<int:index>/support', methods=['POST'])
def send_support_to_webhook(index):
    """Send support notification to a specific webhook"""
    webhooks = config.get("webhooks", [])
    
    if index < 0 or index >= len(webhooks):
        return jsonify({"success": False, "message": "Invalid webhook index"}), 400
    
    webhook = webhooks[index]
    webhook_url = webhook.get("url", "")
    webhook_name = webhook.get("name", "Webhook")
    
    if not webhook_url:
        return jsonify({"success": False, "message": "Webhook URL is empty"})
    
    payload = get_support_payload()
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            return jsonify({"success": True, "message": f"Support notification sent to {webhook_name}"})
        else:
            return jsonify({"success": False, "message": f"Webhook returned {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/api/send-support-notification', methods=['POST'])
def send_support_notification():
    """Send a support/donation reminder notification to all webhooks"""
    webhooks = config.get("webhooks", [])
    webhook_urls = [w.get("url") for w in webhooks if w.get("url")]
    
    if not webhook_urls:
        return jsonify({"success": False, "message": "No webhooks configured"})
    
    payload = get_support_payload()
    
    success_count = 0
    errors = []
    
    for url in webhook_urls:
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                success_count += 1
            else:
                errors.append(f"Webhook returned {response.status_code}")
        except Exception as e:
            errors.append(str(e))
    
    if success_count > 0:
        msg = f"Support notification sent to {success_count} webhook(s)"
        if errors:
            msg += f" ({len(errors)} failed)"
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "message": f"All webhooks failed: {', '.join(errors[:3])}"})


@app.route('/api/clear-codes', methods=['POST'])
def clear_codes():
    """Clear sent codes history"""
    global sent_codes, code_expiration_data
    
    data = request.json
    game = data.get("game")
    
    if game and game in sent_codes:
        sent_codes[game] = []
        code_expiration_data[game] = {}
    else:
        sent_codes = {"genshin": [], "starrail": [], "zenless": []}
        code_expiration_data = {"genshin": {}, "starrail": {}, "zenless": {}}
    
    save_sent_codes()
    return jsonify({"success": True, "message": "Codes cleared"})


# Initialize on module load (for gunicorn)
print("Starting HoYoLab Code Notifier...")
load_config()
load_sent_codes()
start_checker()

if __name__ == '__main__':
    # Run Flask development server (only when running directly)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
