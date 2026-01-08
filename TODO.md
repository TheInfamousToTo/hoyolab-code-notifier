# TODO - Future Improvements

## ~~1. Multi-Webhook Support~~ ✅ COMPLETED
Allow users to configure multiple Discord webhooks per game. This would enable:
- Different channels for different games
- Separate webhooks for personal vs server notifications
- Backup webhooks in case primary fails

**Implementation:**
- Update config to support array of webhooks per game
- Add webhook management UI (add/remove/test individual webhooks)
- Send notifications to all configured webhooks for each game

---

## ~~2. Code Expiration Tracking~~ ✅ COMPLETED
Display and notify about code expiration dates:
- Show expiration date in Discord notifications
- Add "expiring soon" warnings (e.g., 24 hours before)
- Display countdown timer in the web GUI
- Color-code codes by urgency (green/yellow/red)

**Implementation:**
- Parse expiration data from API (if available)
- Add scheduled check for expiring codes
- Update Discord embed to include expiration info
- Add visual indicators in GUI

---

## 3. Telegram Integration
Add Telegram bot support alongside Discord:
- Send notifications via Telegram bot
- Support both Discord and Telegram simultaneously
- Telegram-specific formatting with inline buttons for redeem links

**Implementation:**
- Add Telegram bot token configuration
- Create Telegram notification function
- Add toggle in GUI for Telegram notifications
- Support Telegram markdown formatting

---

## 4. Support Notification (On-Demand)
Deploy an optional "support reminder" notification to encourage users to support the project:
- Send a friendly reminder about supporting the project creator
- Include links to GitHub (star the repo), Ko-fi, Buy Me a Coffee, PayPal
- Make it configurable (enable/disable, frequency)
- Can be triggered manually or automatically (e.g., weekly/monthly)

**Implementation:**
- Add support notification endpoint `/api/send-support-notification`
- Create a visually appealing Discord embed with:
  - Project appreciation message
  - GitHub repo link (for starring)
  - Ko-fi link: https://ko-fi.com/theinfamoustoto
  - Buy Me a Coffee link: https://www.buymeacoffee.com/theinfamoustoto
  - PayPal link: https://paypal.me/alsatrawi
  - GitHub Sponsors: https://github.com/sponsors/TheInfamousToTo
- Add "Send Support Reminder" button in the GUI
- Optional: Auto-send support notification on a configurable schedule (default: disabled)
- Add config option `support_notification_enabled` and `support_notification_interval`

**Message Example:**
```
🌟 Enjoying HoYoLab Code Notifier?

This project is developed and maintained by TheInfamousToTo!
If you find it useful, consider showing your support:

⭐ Star on GitHub - It helps others discover this project!
☕ Buy Me a Coffee
❤️ Support on Ko-fi
💳 Donate via PayPal

Every bit of support helps keep this project alive and improving!
Thank you for using HoYoLab Code Notifier! 🎮
```
