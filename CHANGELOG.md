# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
