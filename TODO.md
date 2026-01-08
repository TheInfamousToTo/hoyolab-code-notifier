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

## ~~4. Support Notification (On-Demand)~~ ✅ COMPLETED
Deploy an optional "support reminder" notification to encourage users to support the project:
- ✅ Send a friendly reminder about supporting the project creator
- ✅ Include links to GitHub (star the repo), Ko-fi, Buy Me a Coffee, PayPal
- ✅ Send to all webhooks at once OR individual webhooks
- ✅ Modern Discord embed with organized fields layout

**Implemented Features:**
- Global "Send Support Reminder" button for all webhooks
- Per-webhook support button (golden heart) for individual webhooks
- Beautiful confirmation modal in the web UI
- Genshin Impact UID for in-game Genesis Crystal gifts

---

## 5. Code Statistics Dashboard
Add a statistics section to track code redemption history:
- Total codes discovered per game
- Codes discovered this week/month
- Graph showing code frequency over time
- Export statistics as CSV/JSON

**Implementation:**
- Store code discovery timestamps in sent_codes.json
- Add statistics endpoint `/api/statistics`
- Create dashboard section in the web GUI
- Add chart.js or similar for visualizations

---

## 6. Email Notifications
Add email notification support alongside Discord:
- SMTP configuration for sending emails
- HTML email templates matching Discord embed style
- Option to send to multiple email addresses
- Digest mode: batch codes into periodic summary emails

**Implementation:**
- Add SMTP settings (server, port, username, password)
- Create email notification templates
- Add email configuration section in GUI
- Support both instant and digest notification modes

---

## 7. Code Auto-Redemption
Automatically redeem codes on HoYoLab accounts:
- Link HoYoLab accounts via cookies/tokens
- Auto-redeem new codes when discovered
- Support multiple accounts per game
- Redemption status tracking and notifications

**Implementation:**
- Add HoYoLab account configuration
- Implement redemption API calls for each game
- Add account management UI
- Track redemption success/failure per account
- Send redemption status notifications
