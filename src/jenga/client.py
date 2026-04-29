from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .config import JengaConfig
from .exceptions import JengaConfigError, JengaRequestError, JengaSignatureError


@dataclass
class JengaClient:
    config: JengaConfig

    @classmethod
    def from_env(cls) -> "JengaClient":
        return cls(config=JengaConfig.from_env())

    def access_token(self) -> str:
        payload = {
            "merchantCode": self.config.merchant_code,
            "consumerSecret": self.config.consumer_secret,
        }
        response = self._request(
            method="POST",
            path="/authentication/api/v3/authenticate/merchant",
            headers={
                "Api-Key": self.config.api_key,
                "Content-Type": "application/json",
            },
            body=payload,
        )

        token = response.get("accessToken")
        if not token:
            raise JengaRequestError("Authentication response did not include accessToken")
        return str(token)

    def sign(self, *parts: str) -> str:
        data_to_sign = "".join(parts)
        if not data_to_sign:
            raise JengaSignatureError("Nothing to sign")

        try:
            private_key = serialization.load_pem_private_key(
                self.config.private_key.encode("utf-8"),
                password=None,
            )
            signature = private_key.sign(
                data_to_sign.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except (TypeError, ValueError) as exc:
            raise JengaSignatureError(f"Failed to load private key: {exc}") from exc

        return base64.b64encode(signature).decode("ascii")

    def account_balance(self, country_code: str | None = None, account_id: str | None = None) -> dict[str, Any]:
        country_code = _required_value(country_code, "country_code")
        account_id = _required_value(account_id, "account_id")
        token = self.access_token()
        signature = self.sign(country_code, account_id)

        return self._request(
            method="GET",
            path=f"/v3-apis/account-api/v3.0/accounts/balances/{country_code}/{account_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "signature": signature,
            },
        )

    def mini_statement(self, country_code: str | None = None, account_id: str | None = None) -> dict[str, Any]:
        country_code = _required_value(country_code, "country_code")
        account_id = _required_value(account_id, "account_id")
        token = self.access_token()
        signature = self.sign(country_code, account_id)

        return self._request(
            method="GET",
            path=f"/v3-apis/account-api/v3.0/accounts/miniStatement/{country_code}/{account_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "signature": signature,
            },
        )

    def _request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.config.base_url.rstrip('/')}{path}"
        data = None

        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = request.Request(url=url, data=data, method=method)
        for key, value in headers.items():
            req.add_header(key, value)

        try:
            with request.urlopen(req) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise JengaRequestError(f"HTTP {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise JengaRequestError(f"Request failed: {exc.reason}") from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise JengaRequestError("Response was not valid JSON") from exc

        if not isinstance(parsed, dict):
            raise JengaRequestError("Expected a JSON object response")

        return parsed


def _required_value(value: str | None, name: str) -> str:
    if value:
        return value
    raise JengaConfigError(f"{name} is required for this endpoint")
