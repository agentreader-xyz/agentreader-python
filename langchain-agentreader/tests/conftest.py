import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

SEEN = []


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        SEEN.append({"path": urlparse(self.path).path, "q": q, "auth": self.headers.get("Authorization"), "ua": self.headers.get("User-Agent")})
        url = q.get("url", [""])[0]
        if "limit" in url:
            return self._send(402, {"error": "Free limit reached", "code": "free_limit"})
        if "blocked" in url:
            return self._send(502, {"error": "Site returned a bot challenge", "code": "upstream", "reason": "bot_challenge"})
        body = {"url": url + "/final", "title": "T", "author": None, "lang": "en", "contentType": "pdf" if url.endswith(".pdf") else "html",
                "pageType": "article", "wordCount": 3, "markdown": "# T\n\nhello world", "text": "T hello world",
                "meta": {"pages": 2 if url.endswith(".pdf") else None, "renderedWithBrowser": False},
                "fields": {"price": "9"} if "extract" in q else None}
        self._send(200, body, {"x-agentreader-tier": "free-anon", "x-agentreader-remaining": "4"})

    def _send(self, status, body, headers=None):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)


@pytest.fixture()
def server(monkeypatch):
    monkeypatch.delenv("AGENTREADER_API_KEY", raising=False)
    s = HTTPServer(("127.0.0.1", 0), H)
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    SEEN.clear()
    yield f"http://127.0.0.1:{s.server_port}", SEEN
    s.shutdown()
