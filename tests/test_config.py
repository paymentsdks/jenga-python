import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


SRC_PATH = Path(__file__).resolve().parents[1] / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from jenga.config import JengaConfig
from jenga.exceptions import JengaConfigError


class JengaConfigTests(unittest.TestCase):
    def test_from_env_loads_values(self) -> None:
        env = {
            "JENGA_API_KEY": "api-key",
            "JENGA_MERCHANT_CODE": "merchant",
            "JENGA_CONSUMER_SECRET": "secret",
            "JENGA_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\\nprivate\\n-----END PRIVATE KEY-----",
        }

        with patch.dict(os.environ, env, clear=True):
            config = JengaConfig.from_env()

        self.assertEqual(config.api_key, "api-key")
        self.assertEqual(config.merchant_code, "merchant")
        self.assertEqual(config.consumer_secret, "secret")
        self.assertEqual(config.private_key, "-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----")
        self.assertEqual(config.base_url, "https://uat.finserve.africa")

    def test_from_env_uses_live_url_when_live_mode_is_true(self) -> None:
        env = {
            "JENGA_API_KEY": "api-key",
            "JENGA_MERCHANT_CODE": "merchant",
            "JENGA_CONSUMER_SECRET": "secret",
            "JENGA_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\\nprivate\\n-----END PRIVATE KEY-----",
            "JENGA_LIVE_MODE": "true",
        }

        with patch.dict(os.environ, env, clear=True):
            config = JengaConfig.from_env()

        self.assertEqual(config.base_url, "https://api.finserve.africa")

    def test_from_env_raises_for_missing_required_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(JengaConfigError) as context:
                JengaConfig.from_env()

        self.assertIn("JENGA_API_KEY", str(context.exception))
        self.assertIn("JENGA_PRIVATE_KEY", str(context.exception))
