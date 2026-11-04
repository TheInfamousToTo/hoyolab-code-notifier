"""Regression tests for access control, configuration and webhook delivery."""
import base64
import hashlib
import hmac
import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Setup must happen before importing app: Gunicorn-style startup loads state.
TEST_DIR = tempfile.TemporaryDirectory()
os.environ["CONFIG_PATH"] = str(Path(TEST_DIR.name) / "config.json")
os.environ["CODES_PATH"] = str(Path(TEST_DIR.name) / "sent_codes.json")
os.environ["ADMIN_TOKEN"] = "test-token-with-at-least-32-characters"
notifier = importlib.import_module("app")
notifier.stop_checker.set()
CSRF = hmac.digest(
    os.environ["ADMIN_TOKEN"].encode(),
    b"hoyolab-code-notifier-csrf-v1", "sha256"
).hex()
AUTH = "Basic " + base64.b64encode(
    ("admin:" + os.environ["ADMIN_TOKEN"]).encode()
).decode()
VALID_URL = "https://discord.com/api/webhooks/123456789/token_abc-123.DEF"


class DashboardSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = notifier.app.test_client()
        notifier.config["webhooks"] = []
        self.headers = {"Authorization": AUTH, "X-CSRF-Token": CSRF}
        self.read_headers = {"Authorization": AUTH}

    def test_healthcheck_is_public_and_non_sensitive(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})

    def test_read_and_html_require_authentication(self):
        self.assertEqual(self.client.get("/").status_code, 401)
        self.assertEqual(self.client.get("/api/config").status_code, 401)
        self.assertEqual(self.client.get("/", headers=self.read_headers).status_code, 200)

    def test_csrf_required_for_mutations(self):
        result = self.client.post("/api/config", json={"check_interval": 900},
                                  headers=self.read_headers)
        self.assertEqual(result.status_code, 403)

    def test_config_validation_is_atomic(self):
        previous = notifier.config["check_interval"]
        result = self.client.post(
            "/api/config", json={"check_interval": "not-a-number"},
            headers=self.headers
        )
        self.assertEqual(result.status_code, 400)
        self.assertEqual(notifier.config["check_interval"], previous)

    def test_invalid_timezone_returns_400(self):
        result = self.client.post(
            "/api/config", json={"timezone": "Unreal/Nowhere"}, headers=self.headers
        )
        self.assertEqual(result.status_code, 400)

    def test_invalid_discord_targets_rejected(self):
        invalid = [
            "http://discord.com/api/webhooks/1/token",
            "https://127.0.0.1/internal",
            "https://discord.com.evil.invalid/api/webhooks/1/token",
            "https://discord.com@evil.invalid/api/webhooks/1/token",
            "https://discord.com:8443/api/webhooks/1/token",
            "https://discord.com/api/webhooks/1/token?x=1",
        ]
        for target in invalid:
            with self.subTest(target=target):
                result = self.client.post(
                    "/api/webhooks",
                    json={"name": "example", "url": target,
                          "games": {"genshin": True}},
                    headers=self.headers
                )
                self.assertEqual(result.status_code, 400)

    def test_valid_webhook_and_duplicate_refused(self):
        data = {"name": "<img src=x onerror=alert(1)>",
                "url": VALID_URL, "games": {"genshin": True}}
        response = self.client.post("/api/webhooks", json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api/webhooks", json=data, headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_unvalidated_test_url_cannot_be_used_for_ssrf(self):
        response = self.client.post("/api/test-webhook",
                                    json={"webhook_url": "http://127.0.0.1:8000"},
                                    headers=self.headers)
        self.assertFalse(response.json["success"])

    def test_local_statistics(self):
        result = self.client.get("/api/dashboard-summary", headers=self.read_headers)
        self.assertEqual(result.status_code, 200)
        self.assertIn("total_codes", result.json)
        self.assertEqual(len(self.client.get("/api/statistics/frequency?days=5",
                               headers=self.read_headers).json["daily"]), 5)

    def test_retries_failed_webhooks_without_repeating_success(self):
        other = "https://discord.com/api/webhooks/123456789/second_token.abc"
        notifier.config["webhooks"] = [
            {"name": "primary", "url": VALID_URL, "games": {"genshin": True}},
            {"name": "backup", "url": other, "games": {"genshin": True}},
        ]
        notifier.delivered_by_webhook.clear()
        data = {"code": "HAPPYTEST", "rewards": []}
        with patch.object(notifier, "post_discord_webhook") as send, \
             patch.object(notifier.time, "sleep"):
            send.side_effect = [Mock(status_code=204), Mock(status_code=500),
                                Mock(status_code=204)]
            self.assertFalse(notifier.send_discord_notification("genshin", data))
            self.assertTrue(notifier.send_discord_notification("genshin", data))
            self.assertEqual(send.call_count, 3)
            self.assertEqual(send.call_args.args[0], other)


if __name__ == "__main__":
    unittest.main()
