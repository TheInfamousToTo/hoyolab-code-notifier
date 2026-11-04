"""Access controls and Discord-only webhook validation.

The dashboard is intentionally protected by default. The generated password is
stored next to the application configuration if ADMIN_TOKEN is not provided.
"""
import hmac
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urlsplit

import requests
from flask import Response, jsonify, request


WEBHOOK_PATTERN = re.compile(r"^/api/webhooks/[0-9]+/[A-Za-z0-9_.-]+$")
VALID_DISCORD_HOSTS = {"discord.com", "discordapp.com"}


def validate_discord_url(value):
    """Accept only official HTTPS Discord webhook endpoints (no redirects)."""
    if not isinstance(value, str) or len(value) > 512:
        return False
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == "https"
            and parsed.hostname in VALID_DISCORD_HOSTS
            and parsed.netloc == parsed.hostname
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
            and bool(WEBHOOK_PATTERN.fullmatch(parsed.path))
        )
    except (ValueError, TypeError):
        return False


def normalize_webhook(raw):
    if not isinstance(raw, dict):
        raise ValueError("Webhook must be an object")
    url = raw.get("url")
    if not validate_discord_url(url):
        raise ValueError("Use an official https://discord.com/api/webhooks/... URL")
    name = raw.get("name", "Webhook")
    if not isinstance(name, str) or len(name.strip()) > 80:
        raise ValueError("Webhook name must be 80 characters or fewer")
    games = raw.get("games", {})
    if not isinstance(games, dict) or any(
        key not in {"genshin", "starrail", "zenless"} or not isinstance(val, bool)
        for key, val in games.items()
    ):
        raise ValueError("Games must contain supported game names and boolean toggles")
    return {
        "name": name.strip() or "Webhook",
        "url": url,
        "games": {game: games.get(game, False) for game in ("genshin", "starrail", "zenless")},
    }


def normalize_webhooks(items):
    if not isinstance(items, list) or len(items) > 30:
        raise ValueError("Webhooks must be a list of at most 30 entries")
    normalized = [normalize_webhook(item) for item in items]
    urls = [item["url"] for item in normalized]
    if len(urls) != len(set(urls)):
        raise ValueError("Duplicate webhook URLs are not allowed")
    return normalized


def post_discord_webhook(url, payload):
    if not validate_discord_url(url):
        raise ValueError("Invalid Discord webhook URL")
    return requests.post(url, json=payload, timeout=10, allow_redirects=False)


def _load_admin_token():
    explicit = os.environ.get("ADMIN_TOKEN")
    if explicit:
        if len(explicit) < 16:
            raise RuntimeError("ADMIN_TOKEN must contain at least 16 characters")
        return explicit
    config_path = os.environ.get("CONFIG_PATH", "/app/data/config.json")
    path = Path(os.environ.get("ADMIN_TOKEN_PATH", str(Path(config_path).parent / "admin_token")))
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(secrets.token_urlsafe(32) + "\n")
        print(f"Dashboard login: username admin; password stored at {path}", flush=True)
    except FileExistsError:
        pass
    return path.read_text(encoding="utf-8").strip()


def configure_security(app):
    """Authenticate all dashboard/API routes except a non-sensitive healthcheck."""
    password = _load_admin_token()
    csrf = hmac.digest(password.encode(), b"hoyolab-code-notifier-csrf-v1", "sha256").hex()
    app.jinja_env.globals["csrf_token"] = csrf
    app.config["MAX_CONTENT_LENGTH"] = 65536

    @app.before_request
    def protect_dashboard():
        if request.path == "/health":
            return None
        auth = request.authorization
        bearer = request.headers.get("Authorization", "")
        authenticated = (
            auth is not None
            and auth.type.lower() == "basic"
            and auth.username == "admin"
            and hmac.compare_digest(auth.password or "", password)
        ) or (
            bearer.startswith("Bearer ")
            and hmac.compare_digest(bearer[7:], password)
        )
        if not authenticated:
            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="HoYoLab Code Notifier", charset="UTF-8"'},
            )
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            if not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), csrf):
                return jsonify({"success": False, "message": "Invalid CSRF token"}), 403
        return None

    @app.after_request
    def secure_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
