# TODO - Future Improvements

## 1. Multi-Webhook Support
Allow users to configure multiple Discord webhooks per game. This would enable:
- Different channels for different games
- Separate webhooks for personal vs server notifications
- Backup webhooks in case primary fails

**Implementation:**
- Update config to support array of webhooks per game
- Add webhook management UI (add/remove/test individual webhooks)
- Send notifications to all configured webhooks for each game

---

## 2. Code Expiration Tracking
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
