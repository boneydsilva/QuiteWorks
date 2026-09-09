"""Point the whole site at a new address, in one command.

    python tools/set-site-url.py https://quietworks.pages.dev
    python tools/set-site-url.py https://www.quietworks.in

Rewrites the absolute site URL wherever it is baked in: the canonical link,
og:url and og:image on every page, the Sitemap line in robots.txt, and every
<loc> in sitemap.xml. Paths are preserved; only the scheme and host change.

The current address is read from index.html's canonical tag, so this is safe to
run repeatedly. Pass --check to see what is set now without changing anything.
"""
import io
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
PAGES = ["index.html", "workqueue.html", "pricing.html", "contact.html"]
OTHERS = ["robots.txt", "sitemap.xml"]


def read(name):
    with io.open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def write(name, text):
    with io.open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def current_base():
    m = re.search(r'<link rel="canonical" href="(https?://[^/"]+)', read("index.html"))
    if not m:
        sys.exit("Could not find a canonical tag in index.html - has it been edited?")
    return m.group(1)


def main():
    args = [a for a in sys.argv[1:] if a]
    old = current_base()

    if not args or args[0] == "--check":
        print("current site URL: " + old)
        return

    new = args[0].rstrip("/")
    if not re.match(r"^https?://[^/]+$", new):
        sys.exit("Give a bare origin, e.g. https://quietworks.pages.dev (no path)")
    if new == old:
        print("Already set to " + new + " - nothing to do.")
        return

    changed = 0
    for name in PAGES + OTHERS:
        text = read(name)
        if old not in text:
            continue
        hits = text.count(old)
        write(name, text.replace(old, new))
        print("  %-16s %d replaced" % (name, hits))
        changed += hits

    if not changed:
        sys.exit("Found nothing to replace - is '%s' really the current URL?" % old)

    print("\n%s  ->  %s   (%d references)" % (old, new, changed))
    print("Commit and push, and Cloudflare will rebuild.")


if __name__ == "__main__":
    main()
