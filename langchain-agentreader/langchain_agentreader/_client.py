"""Minimal HTTP client for the AgentReader REST API (https://agentreader.xyz)."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

DEFAULT_BASE_URL = "https://agentreader.xyz"
API_KEY_ENV = "AGENTREADER_API_KEY"
BASE_URL_ENV = "AGENTREADER_BASE_URL"


class AgentReaderError(RuntimeError):
    """Raised when AgentReader returns an error (bad input, bot check, free limit, ...).

    AgentReader does not charge for failed reads (blocked by a bot check, paywalled, upstream errors).
    """

    def __init__(self, message: str, status: int, code: Optional[str] = None, reason: Optional[str] = None, url: Optional[str] = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.reason = reason
        self.url = url


class AgentReaderClient:
    """Calls ``GET /v1/read?format=json``.

    Without an API key you get the free tier (5 reads/day per IP). Set ``AGENTREADER_API_KEY``
    (or pass ``api_key``) to use prepaid credits from https://agentreader.xyz/buy.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 90.0,
                 user_agent: str = "agentreader-python", session: Optional[requests.Session] = None):
        self.api_key = api_key if api_key is not None else os.environ.get(API_KEY_ENV) or None
        self.base_url = (base_url or os.environ.get(BASE_URL_ENV) or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = session or requests.Session()

    def _headers(self) -> Dict[str, str]:
        h = {"Accept": "application/json", "User-Agent": self.user_agent}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def read(self, url: str, mode: Optional[str] = None, render: Optional[str] = None,
             extract: Optional[str] = None, nocache: bool = False) -> Dict[str, Any]:
        """Read one URL (web page, feed or PDF). Returns the JSON body plus a ``_usage`` dict."""
        params: Dict[str, str] = {"url": url, "format": "json"}
        if mode:
            params["mode"] = mode
        if render:
            params["render"] = render
        if extract:
            params["extract"] = extract
        if nocache:
            params["nocache"] = "1"
        resp = self.session.get(f"{self.base_url}/v1/read", params=params, headers=self._headers(), timeout=self.timeout)
        try:
            body = resp.json()
        except ValueError:
            body = {}
        if resp.status_code >= 400 or not isinstance(body, dict) or "error" in body and "markdown" not in body:
            msg = body.get("error") if isinstance(body, dict) else None
            if resp.status_code == 402:
                msg = (msg or "Payment required") + (
                    " Free tier is 5 reads/day without a key. Buy credits at "
                    f"{self.base_url}/buy and set {API_KEY_ENV}."
                )
            raise AgentReaderError(msg or f"HTTP {resp.status_code}", resp.status_code,
                                   body.get("code") if isinstance(body, dict) else None,
                                   body.get("reason") if isinstance(body, dict) else None, url)
        body["_usage"] = {
            "tier": resp.headers.get("x-agentreader-tier"),
            "remaining": resp.headers.get("x-agentreader-remaining"),
            "tokens": resp.headers.get("x-agentreader-tokens"),
        }
        return body
