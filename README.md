# HoYoLab Code Notifier

[![Docker Build](https://github.com/TheInfamousToTo/hoyolab-code-notifier/actions/workflows/docker-build.yml/badge.svg)](https://github.com/TheInfamousToTo/hoyolab-code-notifier/actions/workflows/docker-build.yml)
[![GitHub release](https://img.shields.io/github/v/release/TheInfamousToTo/hoyolab-code-notifier)](https://github.com/TheInfamousToTo/hoyolab-code-notifier/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/theinfamoustoto/hoyolab-code-notifier)](https://hub.docker.com/r/theinfamoustoto/hoyolab-code-notifier)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automatically monitors for new HoYoLab redemption codes and sends notifications to Discord via webhook.

![HoYoLab Code Notifier](https://img.shields.io/badge/HoYoLab-Code%20Notifier-blue?style=for-the-badge)

## Features

- 🎮 Supports **Genshin Impact**, **Honkai: Star Rail**, and **Zenless Zone Zero**
- 🔔 **Multi-Webhook Support** - Send to multiple Discord channels with per-webhook game selection
- ⏰ **Code Expiration Tracking** - See when codes expire with timezone-aware display
- 💛 **Support Notifications** - Send support reminders globally or per-webhook
- 🎭 Game-specific mascot avatars (Paimon, PomPom, Eous) for Discord notifications
- 🖼️ Official HoYoverse game icons in the UI
- 🚫 Duplicate code prevention - never sends the same code twice
- 🌐 Modern HoYoLab-inspired web GUI for easy configuration
- 🌍 Configurable timezone for expiration display
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
2. Set the check interval (minimum 60 seconds)
3. Configure your timezone for expiration display
4. Click **Add Webhook** to add Discord webhooks
5. For each webhook, toggle which games to receive notifications for
6. Click "Save" to apply settings

### Via Config File

Edit `data/config.json`:

```json
{
  "webhooks": [
    {
      "name": "Main Server",
      "url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
      "games": {
        "genshin": true,
        "starrail": true,
        "zenless": true
      }
    },
    {
      "name": "Genshin Only Channel",
      "url": "https://discord.com/api/webhooks/ANOTHER_WEBHOOK_ID/ANOTHER_TOKEN",
      "games": {
        "genshin": true,
        "starrail": false,
        "zenless": false
      }
    }
  ],
  "check_interval": 300,
  "timezone": "UTC"
}
```

| Option | Description |
|--------|-------------|
| `webhooks` | Array of webhook configurations |
| `webhooks[].name` | Display name for the webhook |
| `webhooks[].url` | Discord webhook URL |
| `webhooks[].games` | Object with game toggles (genshin, starrail, zenless) |
| `check_interval` | How often to check for new codes (in seconds, minimum 60) |
| `timezone` | Timezone for expiration display (e.g., "UTC", "Asia/Tokyo", "America/New_York") |

## Discord Notification Example

When a new code is found, you'll receive a Discord notification with game-specific mascots:

| Game | Mascot | Avatar |
|------|--------|--------|
| Genshin Impact | Paimon | Official game icon |
| Honkai: Star Rail | PomPom | Official game icon |
| Zenless Zone Zero | Eous | Official game icon |

```
🎁 New Code Available for Genshin Impact!

Code: GENSHINGIFT

Rewards: Primogems x60, Mora x10000

⏰ Expires: Jan 15, 2026 at 11:59 PM (UTC)

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
| `/api/webhooks` | GET | List all webhooks |
| `/api/webhooks` | POST | Add a new webhook |
| `/api/webhooks/<index>` | PUT | Update a webhook |
| `/api/webhooks/<index>` | DELETE | Delete a webhook |
| `/api/webhooks/<index>/test` | POST | Test a specific webhook |
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

## Star History

<a href="https://www.star-history.com/#TheInfamousToTo/hoyolab-code-notifier&type=Date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TheInfamousToTo/hoyolab-code-notifier&type=Date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TheInfamousToTo/hoyolab-code-notifier&type=Date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=TheInfamousToTo/hoyolab-code-notifier&type=Date&legend=top-left" />
 </picture>
</a>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
