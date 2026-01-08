# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-01-08

### Added

- **Per-Webhook Support Notification**: Send support reminders to individual webhooks
  - Golden heart button on each webhook card
  - Confirmation dialog before sending
  - Works alongside global "Send to All" support notification

### Changed

- Refactored support notification payload into reusable helper function
- Improved code organization for notification endpoints

---

## [1.4.0] - 2026-01-08

### Added

- **Support Notification**: Send support/donation reminders to Discord webhooks
  - Modern Discord embed with organized fields layout
  - Links to GitHub, Ko-fi, Buy Me a Coffee, PayPal, GitHub Sponsors
  - Genshin Impact UID for in-game Genesis Crystal gifts
  - Beautiful confirmation modal in the web UI
- **Star History**: Added Star History chart to README

### Changed

- Improved webhook card button alignment and styling
- Enhanced game toggle buttons with better spacing and icons

### Security

- Updated Flask to 3.1.0
- Updated python-dateutil to 2.9.0.post0
- Updated pytz to 2024.2
- Added Werkzeug 3.1.3, MarkupSafe 3.0.2, Jinja2 3.1.4
- Added certifi and urllib3 with minimum secure versions
- All dependencies updated to latest versions to mitigate known vulnerabilities

## [1.3.0] - 2026-01-08

### Added

- **Multi-Webhook Support**: Configure multiple Discord webhooks with per-webhook game selection
  - Add unlimited webhooks with custom names
  - Enable/disable specific games for each webhook independently
  - Test individual webhooks directly from the UI
  - Edit and delete webhooks easily
- **Code Expiration Tracking**: Display expiration dates in Discord notifications
  - Timezone-aware expiration display (configurable timezone)
  - Visual urgency indicators: critical (red) for <48 hours, warning (yellow) for <7 days
  - Expiration info shown directly in Discord embeds
- **Timezone Configuration**: Set your preferred timezone for expiration display
  - Support for 30+ timezones including Middle East/Gulf region
  - Organized timezone dropdown with regional groups

### Changed

- Configuration structure updated to support webhook arrays
- Removed global webhook URL in favor of multi-webhook system
- Settings card simplified (check interval + timezone only)
- Games are now managed per-webhook instead of globally

### Migration

- Existing configurations are automatically migrated to the new format
- Old `webhook_url` and `games` settings are converted to a single webhook entry

## [1.2.0] - 2026-01-08

### Added

- Game-specific Discord webhook avatars and usernames
  - Genshin Impact: Paimon
  - Honkai: Star Rail: PomPom
  - Zenless Zone Zero: Eous
- Official HoYoverse game icons from HoYoLab CDN
- SVG icons for UI elements (settings, games, history, buttons)
- Live reload of sent codes from JSON file (manual edits now reflect in GUI)

### Changed

- Game icons now display official artwork instead of emojis
- Test webhook now uses Paimon avatar
- Improved game card icon styling with proper image scaling

## [1.1.0] - 2026-01-08

### Changed

- Complete UI redesign with HoYoLab-inspired dark theme
- New modern card-based layout with grid system
- Improved navigation bar with gradient branding
- Enhanced game cards with unique icons and color accents
- Better toggle switches with smooth animations
- Redesigned status bar with pulse animation
- New toast notifications with type indicators
- Added Inter font for better typography
- Subtle background gradient effects
- Improved mobile responsiveness

## [1.0.1] - 2026-01-08

### Fixed

- Fixed Genshin UID dropdown disappearing before copy button could be clicked
- Improved hover interaction with invisible bridge technique

### Security

- Updated requests to 2.32.4 (CVE-2024-47081 fix)

## [1.0.0] - 2026-01-08

### Added

- Initial release
- Support for Genshin Impact, Honkai: Star Rail, and Zenless Zone Zero
- Discord webhook notifications with rich embeds
- Web GUI for configuration
- Config file support for manual configuration
- Duplicate code prevention
- Docker support with health checks
- Configurable check intervals
