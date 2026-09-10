"""Preview the site locally the way Cloudflare Pages serves it.

    python tools/preview.py            # http://localhost:8000
    python tools/preview.py 9000       # a different port

The site uses clean URLs (/workqueue, not /workqueue.html) because that is what
Cloudflare Pages serves. Python's plain http.server does not understand those
and returns 404, so this adds the one rule Pages applies: try the path, then
path.html, then path/index.html. It also serves 404.html with a real 404, and
answers Range requests - without those a <video> can play from the start but
cannot be seeked, which Cloudflare allows and the plain server does not.
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

    def do_GET(self):
        """Serve a byte range when one is asked for; otherwise the usual way."""
        header = self.headers.get("Range")
        path = self.translate_path(self.path.split("?", 1)[0].split("#", 1)[0])
        if not header or not header.startswith("bytes=") or not os.path.isfile(path):
            return super().do_GET()

        size = os.path.getsize(path)
        first, _, last = header[6:].partition("-")
        try:
            start = int(first) if first else max(0, size - int(last))
            end = int(last) if (last and first) else size - 1
        except ValueError:
            return super().do_GET()
        end = min(end, size - 1)
        if start > end:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = f.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def end_headers(self):
        # Tells the browser it may seek at all.
        if self.command in ("GET", "HEAD"):
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

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
