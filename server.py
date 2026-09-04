#!/usr/bin/env python3
"""Sirve el sitio estático del repertorio.

Railway asigna el puerto por la variable PORT; en local cae a 8090.
"""
import http.server
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        "": "application/octet-stream",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        # El sitio se regenera con cada deploy; sin esto el navegador se queda
        # con la versión vieja después de corregir una tab o un análisis.
        self.send_header("Cache-Control", "public, max-age=300, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8090))
    print(f"sirviendo {ROOT} en :{port}", flush=True)
    http.server.HTTPServer(("0.0.0.0", port), Handler).serve_forever()
