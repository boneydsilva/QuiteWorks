"""Point the whole site at a new address, in one command.

    python tools/set-site-url.py https://quietworks.pages.dev
    python tools/set-site-url.py https://www.quietworks.in
    python tools/set-site-url.py --check        # just print the current one

Rewrites the absolute site URL wherever it is baked in: the canonical link,
the hreflang alternates, og:url and og:image and the JSON-LD on all 125 pages,
the Sitemap line in robots.txt, every <loc> and <xhtml:link> in sitemap.xml,
and - this is the one that matters - the SITE constant in build_i18n.py, so
the next build does not put the old address back.

Paths are preserved; only the scheme and host change. The current address is
read from index.html's canonical tag, so this is safe to run repeatedly.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "public")
BUILDER = os.path.join(HERE, "build_i18n.py")


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def targets():
    """Every file under public/ that can carry an absolute URL, plus the
    builder that would otherwise regenerate the old one."""
    found = [BUILDER]
    for base, _dirs, files in os.walk(ROOT):
        for name in files:
            if name.endswith((".html", ".xml", ".txt", ".js")):
                found.append(os.path.join(base, name))
    return found


def current_base():
    m = re.search(r'<link rel="canonical" href="(https?://[^/"]+)',
                  read(os.path.join(ROOT, "index.html")))
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

    changed = files = 0
    for path in targets():
        text = read(path)
        if old not in text:
            continue
        hits = text.count(old)
        write(path, text.replace(old, new))
        changed += hits
        files += 1

    if not changed:
        sys.exit("Found nothing to replace - is '%s' really the current URL?" % old)

    print("%s  ->  %s" % (old, new))
    print("%d references across %d files, build_i18n.py included." % (changed, files))
    print("\nRun `python tools/build_i18n.py --check` to confirm, then commit.")


if __name__ == "__main__":
    main()
