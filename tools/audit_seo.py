# -*- coding: utf-8 -*-
"""Audit every page in public/ without a browser.

    python tools\audit_seo.py

Checks, for all 125 pages: exactly one <h1>, a title of a sane length, a
description, a canonical that matches where the file actually is, that every
internal link resolves to a real file, that the hreflang sets are
self-referential and reciprocal, and that the sitemap and the tree agree.

Run it after tools/build_i18n.py. It is the cheap half of the checks - see
tools/check_console.py for the half that needs Chrome.
"""
import io
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
SITE = "https://boneydsilva.com"
problems = []


def note(msg):
    problems.append(msg)


def pages():
    for base, _dirs, files in os.walk(ROOT):
        if "assets" in base:
            continue
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(base, f)


def url_of(path):
    """Match what build_i18n.url_for() produces: anything backed by an
    index.html keeps its trailing slash ("/", "/hi/", "/india/"); a page
    backed by its own .html file does not ("/pricing")."""
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        # Anything backed by an index.html is served at the slashed URL;
        # Cloudflare 307s the bare form.
        return "/" + rel[: -len("index.html")]
    return "/" + rel[: -len(".html")]


def resolves(url):
    """Does this site-relative URL correspond to a real file?"""
    u = url.split("#")[0].split("?")[0]
    if not u.startswith("/"):
        return True                       # mailto:, https:, #anchor
    if u.startswith("/assets/"):
        return os.path.exists(os.path.join(ROOT, *u.strip("/").split("/")))
    rel = u.strip("/")
    cands = []
    if rel:
        cands += [os.path.join(ROOT, *(rel.split("/"))) + ".html",
                  os.path.join(ROOT, *(rel.split("/")), "index.html")]
    else:
        cands.append(os.path.join(ROOT, "index.html"))
    return any(os.path.exists(c) for c in cands)


all_urls = set()
alts_by_page = {}

docs = sorted(pages())
for path in docs:
    url = url_of(path)
    all_urls.add(url)
    html = io.open(path, encoding="utf-8").read()

    if html.count("<h1") != 1 and "404" not in path:
        note("%s has %d <h1>" % (url, html.count("<h1")))

    if "<title>" not in html:
        note("%s has no <title>" % url)
    else:
        title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
        if len(title) > 75:
            note("%s title is %d chars: %s" % (url, len(title), title[:60]))

    desc = re.search(r'<meta name="description" content="(.*?)">', html, re.S)
    if not desc and "404" not in path:
        note("%s has no meta description" % url)
    elif desc and not (70 <= len(desc.group(1)) <= 320):
        note("%s description is %d chars" % (url, len(desc.group(1))))

    if "404" not in path:
        can = re.search(r'<link rel="canonical" href="([^"]+)">', html)
        if not can:
            note("%s has no canonical" % url)
        else:
            want = SITE + url
            got = can.group(1)
            if got.rstrip("/") != want.rstrip("/"):
                note("%s canonical is %s" % (url, got))

    # internal links
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(("http", "mailto:", "#", "tel:")):
            continue
        if not resolves(href):
            note("%s links to missing %s" % (url, href))

    # hreflang set
    alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', html)
    alts = [(c, h) for c, h in alts if c != "x-default"]
    if alts:
        alts_by_page[url] = {c: h.replace(SITE, "") for c, h in alts}
        for _c, h in alts:
            if not h.startswith(SITE):
                note("%s alternate is not absolute: %s" % (url, h))
            elif not resolves(h.replace(SITE, "")):
                note("%s alternate points at missing %s" % (url, h))
    elif "404" not in path:
        note("%s has no hreflang alternates" % url)

# hreflang must be reciprocal and self-referential
for url, alts in alts_by_page.items():
    if url not in alts.values():
        note("%s is not in its own hreflang set" % url)
    for code, href in alts.items():
        other = alts_by_page.get(href)
        if other is None:
            note("%s points at %s which declares no alternates" % (url, href))
        elif other != alts:
            note("%s and %s disagree on the alternate set" % (url, href))

# sitemap
sm = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
sm_urls = {l.replace(SITE, "") for l in locs}
missing = all_urls - sm_urls - {"/404"}
extra = sm_urls - all_urls
if missing:
    note("not in sitemap: %s" % ", ".join(sorted(missing)[:8]))
if extra:
    note("in sitemap but no page: %s" % ", ".join(sorted(extra)[:8]))
if len(locs) != len(set(locs)):
    note("sitemap has duplicate <loc>")

print("%d pages, %d sitemap urls" % (len(docs), len(locs)))
if problems:
    print("\n%d PROBLEMS" % len(problems))
    for p in problems[:40]:
        print("  -", p)
    sys.exit(1)
print("clean")
