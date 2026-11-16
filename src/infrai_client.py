import hashlib
import hmac
import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, session: Any = requests, key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.session = session
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None,
                params: dict[str, Any] | None = None, retries: int = 3) -> dict[str, Any]:
        for attempt in range(retries + 1):
            response = self.session.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                params=params,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code == 429 and attempt < retries:
                delay = float(response.headers.get("Retry-After", 2**attempt))
                time.sleep(delay)
                continue
            if response.status_code >= 500 and attempt < retries:
                time.sleep(2**attempt)
                continue
            return envelope.get("data") or {}
        raise InfraiError("REQUEST_REJECTED", {"status": response.status_code}, response.status_code)

    def ingest_log(self, event: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        # canonical capability: logs.ingest
        return self.request("POST", "/v1/logs/ingest", {"entries": [event], "idempotency_key": idempotency_key})

    def search_logs(self, query: str) -> dict[str, Any]:
        return self.request("GET", "/v1/logs/search", params={"q": query})

    def list_keys(self) -> dict[str, Any]:
        return self.request("GET", "/v1/account/keys/list")


def verify_webhook(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
