# © 1993–2026 Abhishek Choudhary. All rights reserved. AyeAI.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Local desk server. A token stays in this process. It is not written to the venue."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .platform import Platform

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DATA = ROOT / "run"
TOKEN: dict[str, str | None] = {"zenodo": None}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _send(self, code: int, body: dict | str, content_type: str = "application/json") -> None:
        raw = body if isinstance(body, str) else json.dumps(body)
        data = raw.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        # No cross-origin access: the pages are served by this server itself, so they need none.
        self._send(405, {"error": "cross-origin requests are not served"})

    def _same_origin(self) -> bool:
        origin = self.headers.get("Origin")
        host = self.server.server_address
        return origin is None or origin in (f"http://127.0.0.1:{host[1]}", f"http://localhost:{host[1]}")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send(200, {"ok": True, "token_loaded": bool(TOKEN["zenodo"]), "token_written": False})
            return
        if path == "/api/face":
            role = urlparse(self.path).query.split("role=")[-1] or "reader"
            self._send(200, {"role": role, "source": "index", "papers": []})
            return
        if path == "/api/venues":
            venues = [str(p.relative_to(DATA)) for p in DATA.glob("venues/*/*") if p.is_dir()] if DATA.exists() else []
            self._send(200, {"venues": venues})
            return
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        file = (WEB / rel).resolve()
        if not str(file).startswith(str(WEB.resolve())) or not file.is_file():
            self._send(404, {"error": "not found"})
            return
        kind = "text/html" if file.suffix == ".html" else "text/javascript" if file.suffix == ".js" else "text/plain"
        self._send(200, file.read_text(encoding="utf-8"), kind)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not self._same_origin():
            self._send(403, {"error": "a page from another origin may not change this desk"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if path == "/api/token":
            TOKEN["zenodo"] = payload.get("zenodo") or None
            self._send(200, {"loaded": bool(TOKEN["zenodo"]), "stored_in_repo": False})
            return
        if path == "/api/launch":
            platform = Platform(DATA)
            actor = payload.get("actor", "editor")
            if not (DATA / "records" / "person" / f"{actor}.json").exists():
                self._send(403, {"error": "a person without a forge login cannot act"})
                return
            desk = platform.launch(payload["kind"], payload["title"], actor, payload.get("owner", "person"))
            self._send(200, {"venue": str(desk.store.path), "kind": payload["kind"]})
            return
        self._send(404, {"error": "not found"})


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
