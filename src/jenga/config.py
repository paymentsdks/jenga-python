from __future__ import annotations

import os
from dataclasses import dataclass

from .exceptions import JengaConfigError


@dataclass(frozen=True)
class JengaConfig:
    api_key: str
    merchant_code: str
    consumer_secret: str
    private_key: str
    base_url: str

    @classmethod
    def from_env(cls) -> "JengaConfig":
        data = cls(
            api_key=os.environ.get("JENGA_API_KEY", ""),
            merchant_code=os.environ.get("JENGA_MERCHANT_CODE", ""),
            consumer_secret=os.environ.get("JENGA_CONSUMER_SECRET", ""),
            private_key=_normalize_pem(os.environ.get("JENGA_PRIVATE_KEY", "")),
            base_url=_default_base_url(),
        )
        data.validate()
        return data

    def validate(self) -> None:
        missing = []

        if not self.api_key:
            missing.append("JENGA_API_KEY")
        if not self.merchant_code:
            missing.append("JENGA_MERCHANT_CODE")
        if not self.consumer_secret:
            missing.append("JENGA_CONSUMER_SECRET")
        if not self.private_key:
            missing.append("JENGA_PRIVATE_KEY")

        if missing:
            joined = ", ".join(missing)
            raise JengaConfigError(f"Missing required environment variables: {joined}")


def _normalize_pem(value: str) -> str:
    return value.replace("\\n", "\n").strip()


def _env_flag(name: str) -> bool:
    value = os.environ.get(name, "")
    return value.strip().lower() == "true"


def _default_base_url() -> str:
    live_mode = _env_flag("JENGA_LIVE_MODE")

    if live_mode:
        return "https://api.finserve.africa"
    return "https://uat.finserve.africa"
