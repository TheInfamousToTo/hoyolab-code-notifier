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
- � **Code Statistics Dashboard** - Track total codes, weekly/monthly stats, and frequency charts
- 💛 **Support Notifications** - Send support reminders globally or per-webhook
- 🎭 Game-specific mascot avatars (Paimon, PomPom, Eous) for Discord notifications
- 🖼️ Official HoYoverse game icons in the UI
- 🚫 Duplicate code prevention - never sends the same code twice
- 🌐 Modern, responsive command-center dashboard with tactile controls
- 🔒 Admin authentication, CSRF protection, and Discord-only webhook validation
- 🔎 Search and filter code history by game; one-click code copying and redemption
- 🛡️ Per-webhook retry tracking and atomic persisted state
- 🌍 Configurable timezone for expiration display
- 📦 Export statistics as CSV/JSON
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

3. Get your generated dashboard password:
   ```bash
   docker exec hoyolab-code-notifier cat /app/data/admin_token
   ```
   Username is **admin**. Set `ADMIN_TOKEN` to your own strong value (16+ characters) instead if preferred.

4. Access `http://localhost:5050` and sign in as **admin** with that password

5. Configure your Discord webhook URL and enable/disable games

### Manual Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Set a strong password: `export ADMIN_TOKEN='your-secret-password-at-least-16-characters'`
4. Open `http://localhost:5000` and sign in with username **admin**

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
| `/api/webhooks/<index>/support` | POST | Send support reminder to webhook |
| `/api/send-support-notification` | POST | Send support reminder to all webhooks |
| `/api/clear-codes` | POST | Clear sent codes history |
| `/health` | GET | Minimal unauthenticated health check |
| `/api/dashboard-summary` | GET | Local summary statistics |
| `/api/statistics/frequency?days=30` | GET | Daily local code discovery counts |
| `/api/export/csv` | GET | Export code history as CSV |
| `/api/export/json` | GET | Export code history as JSON |

### Statistics (via integrated backend)

The statistics dashboard is now served **locally** from the notifier's persisted code history, with no external statistics service required:

- **Total codes discovered** per game
- **Weekly/Monthly** discovery counts for codes first seen by this release or later (older history has no discovery timestamps)
- **Frequency charts** showing code discovery over time
- **Export** statistics as CSV or JSON

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIG_PATH` | `/app/data/config.json` | Path to config file |
| `CODES_PATH` | `/app/data/sent_codes.json` | Path to sent codes file |
| `PORT` | `5000` | Web server port |
| `ADMIN_TOKEN` | Automatically generated | Password for HTTP Basic authentication; set 16+ characters for predictable deployment |
| `ADMIN_TOKEN_PATH` | `<config directory>/admin_token` | Persisted password file when `ADMIN_TOKEN` is unset |

## Data Persistence

All data is stored in the `data/` directory:
- `config.json` - Configuration settings
- `sent_codes.json` - History of sent codes, per-destination deliveries, expiration dates and discovery timestamps
- `admin_token` - Generated dashboard password (keep private, do not commit)

When using Docker, mount this directory as a volume to persist data.

## Deployment and security

The dashboard and JSON API require admin authentication. All state-changing API
requests from the dashboard include a CSRF token. Only official HTTPS Discord
webhook URLs are permitted, and redirects are not followed.

**After upgrading:** restart the container, retrieve the new `admin_token` from
the persisted `data/` volume (or configure `ADMIN_TOKEN`), then sign in.
Keep your dashboard behind a trusted LAN, Tailscale, or authenticated reverse proxy;
HTTP Basic passwords should not be sent over plaintext HTTP across untrusted
networks. Terminate TLS at a reverse proxy when exposing the service remotely.

Do not commit `data/` or your webhook tokens. Unlike older releases, this
version does not automatically forward discovered code data to an external
statistics server. To run regression tests: `python -m unittest discover -s tests -v`.

## Suggested next features

- Telegram and email destinations with a common, extensible notifier interface
- Expiration-soon reminders with per-channel opt-in and retry-aware scheduling
- Notification delivery logs, rate-limit/backoff handling, and retry queue
- Optional authentication via OIDC or an existing trusted reverse proxy
- Code import/replay and full notification audit trail
- Optional HoYoLab account-based auto redemption (requires careful secret storage,
  explicit user consent, and maintenance as upstream APIs change)

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
