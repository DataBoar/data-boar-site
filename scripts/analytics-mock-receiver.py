#!/usr/bin/env python3
"""Tiny local beacon sink for site analytics smoke (issue #58). Not for production."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "ops" / "evidence" / "site_analytics_58_beacon.jsonl"


class Handler(BaseHTTPRequestHandler):
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            data = {"raw": body.decode("utf-8", errors="replace")}
        with OUT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(data, ensure_ascii=False) + "\n")
        print(f"beacon -> {OUT}: {data}", flush=True)
        self.send_response(204)
        self._cors()
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print(f"listening on http://127.0.0.1:{port}/beacon  writing {OUT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
