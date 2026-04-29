import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


SRC_PATH = Path(__file__).resolve().parents[1] / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from jenga.client import JengaClient
from jenga.config import JengaConfig
from jenga.exceptions import JengaConfigError, JengaRequestError, JengaSignatureError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class JengaClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = JengaConfig(
            api_key="api-key",
            merchant_code="merchant",
            consumer_secret="secret",
            private_key="-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----",
            base_url="https://uat.finserve.africa",
        )
        self.client = JengaClient(config=self.config)

    @patch("jenga.client.request.urlopen")
    def test_access_token_returns_value(self, mock_urlopen) -> None:
        mock_urlopen.return_value = FakeResponse({"accessToken": "token-123"})

        token = self.client.access_token()

        self.assertEqual(token, "token-123")

    @patch("jenga.client.serialization.load_pem_private_key")
    def test_sign_returns_base64_signature(self, mock_load_private_key) -> None:
        mock_private_key = Mock()
        mock_private_key.sign.return_value = b"signed"
        mock_load_private_key.return_value = mock_private_key

        signature = self.client.sign("KE", "123")

        self.assertEqual(signature, "c2lnbmVk")
        mock_private_key.sign.assert_called_once()

    @patch("jenga.client.serialization.load_pem_private_key")
    def test_sign_raises_for_invalid_private_key(self, mock_load_private_key) -> None:
        mock_load_private_key.side_effect = ValueError("bad key")

        with self.assertRaises(JengaSignatureError) as context:
            self.client.sign("KE", "123")

        self.assertIn("bad key", str(context.exception))

    @patch.object(JengaClient, "access_token", return_value="token-123")
    @patch.object(JengaClient, "sign", return_value="signed-value")
    @patch("jenga.client.request.urlopen")
    def test_account_balance_calls_expected_endpoint(self, mock_urlopen, mock_sign, mock_access_token) -> None:
        mock_urlopen.return_value = FakeResponse({"status": "ok"})

        result = self.client.account_balance(country_code="KE", account_id="1450160649886")

        self.assertEqual(result, {"status": "ok"})
        request_obj = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request_obj.full_url,
            "https://uat.finserve.africa/v3-apis/account-api/v3.0/accounts/balances/KE/1450160649886",
        )
        self.assertEqual(request_obj.headers["Authorization"], "Bearer token-123")
        self.assertEqual(request_obj.headers["Signature"], "signed-value")
        mock_sign.assert_called_once_with("KE", "1450160649886")
        mock_access_token.assert_called_once_with()

    def test_account_balance_requires_country_code_and_account_id(self) -> None:
        with self.assertRaises(JengaConfigError) as context:
            self.client.account_balance()

        self.assertIn("country_code is required", str(context.exception))

    @patch.object(JengaClient, "access_token", return_value="token-123")
    @patch.object(JengaClient, "sign", return_value="signed-value")
    @patch("jenga.client.request.urlopen")
    def test_mini_statement_calls_expected_endpoint(self, mock_urlopen, mock_sign, mock_access_token) -> None:
        mock_urlopen.return_value = FakeResponse({"items": []})

        result = self.client.mini_statement(country_code="UG", account_id="999")

        self.assertEqual(result, {"items": []})
        request_obj = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request_obj.full_url,
            "https://uat.finserve.africa/v3-apis/account-api/v3.0/accounts/miniStatement/UG/999",
        )
        self.assertEqual(request_obj.headers["Authorization"], "Bearer token-123")
        self.assertEqual(request_obj.headers["Signature"], "signed-value")
        mock_sign.assert_called_once_with("UG", "999")
        mock_access_token.assert_called_once_with()

    @patch("jenga.client.request.urlopen")
    def test_request_raises_for_invalid_json(self, mock_urlopen) -> None:
        class InvalidJsonResponse:
            def read(self):
                return b"not-json"

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        mock_urlopen.return_value = InvalidJsonResponse()

        with self.assertRaises(JengaRequestError):
            self.client._request(method="GET", path="/test", headers={})
