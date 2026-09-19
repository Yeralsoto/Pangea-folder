#!/usr/bin/env python3
"""Minimal static server for local preview:  python3 serve.py [port]"""
import sys, os, functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4173

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        SimpleHTTPRequestHandler.end_headers(self)
    def log_message(self, fmt, *a):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

if __name__ == "__main__":
    h = functools.partial(Handler, directory=ROOT)
    print("Pangea site: http://localhost:%d" % PORT)
    ThreadingHTTPServer(("127.0.0.1", PORT), h).serve_forever()
