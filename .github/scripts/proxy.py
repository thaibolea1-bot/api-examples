#!/usr/bin/env python3
"""A lightweight local reverse proxy for Google Gemini API in CI.

Intercepts requests sent via GOOGLE_GEMINI_BASE_URL and injects
`"service_tier": "flex"` into the JSON body without modifying sample code.
"""

import http.server
import json
import sys
import urllib.error
import urllib.request

UPSTREAM_HOST = "https://generativelanguage.googleapis.com"


class GeminiFlexProxyHandler(http.server.BaseHTTPRequestHandler):

  def do_POST(self):
    self._proxy_request("POST")

  def do_GET(self):
    self._proxy_request("GET")

  def do_DELETE(self):
    self._proxy_request("DELETE")

  def do_PATCH(self):
    self._proxy_request("PATCH")

  def do_PUT(self):
    self._proxy_request("PUT")

  def _proxy_request(self, method: str):
    content_length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(content_length) if content_length > 0 else b""

    # Intercept JSON requests to inject service_tier: flex
    if method in ("POST", "PATCH", "PUT") and body:
      try:
        data = json.loads(body.decode("utf-8"))
        if isinstance(data, dict) and "service_tier" not in data:
          data["service_tier"] = "flex"
          body = json.dumps(data).encode("utf-8")
      except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    target_url = f"{UPSTREAM_HOST}{self.path}"
    headers = {
        k: v
        for k, v in self.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    if body:
      headers["Content-Length"] = str(len(body))

    req = urllib.request.Request(
        target_url,
        data=body if method in ("POST", "PATCH", "PUT") else None,
        headers=headers,
        method=method,
    )

    try:
      with urllib.request.urlopen(req) as resp:
        self.send_response(resp.status)
        for header, val in resp.headers.items():
          if header.lower() not in ("transfer-encoding", "content-length"):
            self.send_header(header, val)
        # Read and stream response in chunks (supports SSE & large streams)
        self.end_headers()
        while True:
          chunk = resp.read(65536)
          if not chunk:
            break
          self.wfile.write(chunk)
          self.wfile.flush()
    except urllib.error.HTTPError as e:
      self.send_response(e.code)
      for header, val in e.headers.items():
        if header.lower() not in ("transfer-encoding", "content-length"):
          self.send_header(header, val)
      self.end_headers()
      err_data = e.read()
      self.wfile.write(err_data)
      self.wfile.flush()
    except Exception as e:
      self.send_response(500)
      self.end_headers()
      self.wfile.write(f"Proxy Error: {e}".encode("utf-8"))
      self.wfile.flush()

  def log_message(self, format, *args):
    # Log requests concisely
    sys.stderr.write(f"[Gemini-Proxy] {args[0]} {args[1]}\n")
    sys.stderr.flush()


def run_proxy(port: int = 8080):
  server = http.server.ThreadingHTTPServer(
      ("127.0.0.1", port), GeminiFlexProxyHandler
  )
  sys.stderr.write(
      f"[Gemini-Proxy] Started on http://127.0.0.1:{port} (forwarding to"
      f" {UPSTREAM_HOST})\n"
  )
  sys.stderr.flush()
  server.serve_forever()


if __name__ == "__main__":
  port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
  run_proxy(port)
