"""Preview the site locally the way Cloudflare Pages serves it.

    python tools/preview.py            # http://localhost:8000
    python tools/preview.py 9000       # a different port

The site uses clean URLs (/workqueue, not /workqueue.html) because that is what
Cloudflare Pages serves. Python's plain http.server does not understand those
and returns 404, so this adds the one rule Pages applies: try the path, then
path.html, then path/index.html. It also serves 404.html with a real 404.
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def translate_path(self, path):
        full = super().translate_path(path)
        if os.path.isdir(full):
            index = os.path.join(full, "index.html")
            if os.path.exists(index):
                return index
        if not os.path.exists(full):
            if os.path.exists(full + ".html"):
                return full + ".html"
        return full

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            page = os.path.join(ROOT, "404.html")
            if os.path.exists(page):
                with open(page, "rb") as f:
                    body = f.read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
        super().send_error(code, message, explain)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if not os.path.exists(os.path.join(ROOT, "index.html")):
        sys.exit("No index.html under %s" % os.path.abspath(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Serving %s" % os.path.abspath(ROOT))
    print("  http://localhost:%d   (Ctrl+C to stop)\n" % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
