# HoYoLab Code Notifier

[![Docker Build](https://github.com/TheInfamousToTo/hoyolab-code-notifier/actions/workflows/docker-build.yml/badge.svg)](https://github.com/TheInfamousToTo/hoyolab-code-notifier/actions/workflows/docker-build.yml)
[![GitHub release](https://img.shields.io/github/v/release/TheInfamousToTo/hoyolab-code-notifier)](https://github.com/TheInfamousToTo/hoyolab-code-notifier/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/theinfamoustoto/hoyolab-code-notifier)](https://hub.docker.com/r/theinfamoustoto/hoyolab-code-notifier)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automatically monitors for new HoYoLab redemption codes and sends notifications to Discord via webhook.

![HoYoLab Code Notifier](https://img.shields.io/badge/HoYoLab-Code%20Notifier-blue?style=for-the-badge)

## Features

- 🎮 Supports **Genshin Impact**, **Honkai: Star Rail**, and **Zenless Zone Zero**
- 🔔 Discord webhook notifications with rich embedded messages
- 🚫 Duplicate code prevention - never sends the same code twice
- 🌐 Web GUI for easy configuration
- 📁 Config file support for manual configuration
- 🐳 Docker ready for easy deployment
- ⚡ Lightweight and efficient

## Quick Start

### Using Docker Compose (Recommended)

1. Clone or copy the project files

2. Start the container:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface at `http://localhost:5050`

4. Configure your Discord webhook URL and enable/disable games

### Manual Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the web interface at `http://localhost:5000`

## Configuration

### Via Web GUI

1. Open the web interface
2. Enter your Discord webhook URL
3. Set the check interval (minimum 60 seconds)
4. Enable/disable games as needed
5. Click "Save Configuration"

### Via Config File

Edit `data/config.json`:

```json
{
  "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
  "check_interval": 300,
  "games": {
    "genshin": true,
    "starrail": true,
    "zenless": true
  }
}
```

| Option | Description |
|--------|-------------|
| `webhook_url` | Your Discord webhook URL |
| `check_interval` | How often to check for new codes (in seconds, minimum 60) |
| `games.genshin` | Enable/disable Genshin Impact notifications |
| `games.starrail` | Enable/disable Honkai: Star Rail notifications |
| `games.zenless` | Enable/disable Zenless Zone Zero notifications |

## Discord Notification Example

When a new code is found, you'll receive a Discord embed like this:

```
🎁 New Code Available for Genshin Impact!

Code: GENSHINGIFT

Rewards: Primogems x60, Mora x10000

Redeem Link:
https://genshin.hoyoverse.com/en/gift?code=GENSHINGIFT
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/config` | GET | Get current configuration |
| `/api/config` | POST | Update configuration |
| `/api/status` | GET | Get current status and sent codes |
| `/api/check-now` | POST | Manually trigger code check |
| `/api/test-webhook` | POST | Send a test notification |
| `/api/clear-codes` | POST | Clear sent codes history |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIG_PATH` | `/app/data/config.json` | Path to config file |
| `CODES_PATH` | `/app/data/sent_codes.json` | Path to sent codes file |
| `PORT` | `5000` | Web server port |

## Data Persistence

All data is stored in the `data/` directory:
- `config.json` - Configuration settings
- `sent_codes.json` - History of sent codes (prevents duplicates)

When using Docker, mount this directory as a volume to persist data.

## Credits

Code data sourced from [api.ennead.cc](https://api.ennead.cc) (maintained by [torikushiii](https://github.com/torikushiii))

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you find this project helpful, consider supporting:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/theinfamoustoto)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/theinfamoustoto)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/alsatrawi)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
