# -*- coding: utf-8 -*-
"""Generate the translated pages, the /india pages, and the sitemap.

    python tools\\build_i18n.py            # write everything
    python tools\\build_i18n.py --check    # fail if the tree is out of date

This is the one build step the site has, and it exists because 11 languages
times 4 pages plus 36 states is 116 pages that nobody is going to keep in
step by hand. Everything it writes is plain static HTML that Cloudflare
serves directly - open public/hi/pricing.html and it is exactly what a
reader gets. What is generated:

    public/<lang>/index.html          the home page, 11 languages
    public/<lang>/workqueue.html
    public/<lang>/pricing.html
    public/<lang>/contact.html
    public/india/index.html           the hub, in English
    public/india/<state>.html         36 states and union territories
    public/<lang>/india/index.html    the hub, 11 languages
    public/<lang>/india/<state>.html  each state in its own language
    public/sitemap.xml

The four English pages in public/ stay hand-written. This script only
replaces what is between the <!-- qw:... --> markers in them, so the
hreflang block, the language picker and the JSON-LD stay in step with
everything else while the prose does not get regenerated over.

Add a language: tools/content/langs.py, then a strings file. Add a state:
tools/content/states.py. Both are picked up automatically.
"""

import io
import json
import os
import re
import sys
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from content.langs import LANGS, BY_CODE                     # noqa: E402
from content.states import STATES, states_for                # noqa: E402

PUBLIC = os.path.abspath(os.path.join(HERE, "..", "public"))
SITE = "https://boneydsilva.com"
EMAIL = "boneydsilva@gmail.com"
TODAY = "2026-09-10"

STR = {l["code"]: importlib.import_module("content.strings.%s" % l["code"]).S
       for l in LANGS}

# The four pages that exist in every language. `file` is the name under the
# language folder; `key` prefixes its strings in the language files.
CORE = [("home", "index.html"), ("workqueue", "workqueue.html"),
        ("pricing", "pricing.html"), ("contact", "contact.html")]

written = []
CHECK = "--check" in sys.argv      # compare instead of write
stale = []


# --- 1. Small helpers -------------------------------------------------------

def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def url_for(lang, page, slug=None):
    """The public URL of a page. `page` is home/workqueue/pricing/contact/
    india/state."""
    p = "" if lang == "en" else "/" + lang
    if page == "home":
        return (p + "/") if p else "/"
    if page == "state":
        return "%s/india/%s" % (p, slug)
    if page == "india":
        return p + "/india"
    return "%s/%s" % (p, page)


def file_for(url):
    """Where that URL lives on disk, following Cloudflare's clean-URL rule:
    /pricing is pricing.html, but a URL that is a folder - / and /hi/ and
    every /india - is that folder's index.html."""
    rel = url.strip("/")
    if url.endswith("/") or rel == "" or rel.rsplit("/", 1)[-1] == "india":
        rel = (rel + "/index.html").lstrip("/")
    else:
        rel += ".html"
    return os.path.join(PUBLIC, *rel.split("/"))


def write(url, html):
    path = file_for(url)
    rel = os.path.relpath(path, PUBLIC).replace("\\", "/")
    written.append(rel)
    if CHECK:
        old = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old != html:
            stale.append(rel)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)


def fmt(code, key, values):
    """A string with its {state}/{hub}/{lang} placeholders filled in."""
    return STR[code][key].format(**values)


# --- 2. The parts every page shares -----------------------------------------

def hreflang_block(alts, indent="", default="en"):
    """<link rel="alternate"> for each language this exact page exists in."""
    rows = []
    for code, href in alts.items():
        rows.append('%s<link rel="alternate" hreflang="%s" href="%s%s">'
                    % (indent, BY_CODE[code]["hreflang"], SITE, href))
    rows.append('%s<link rel="alternate" hreflang="x-default" href="%s%s">'
                % (indent, SITE, alts[default]))
    return "\n".join(rows)


def head(lang, title, desc, canonical, alts, extra="", og_image=None,
         robots=None, jsonld=None, geo=None):
    ld = ""
    if jsonld:
        ld = ('\n<script type="application/ld+json">%s</script>'
              % json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")))
    geo_meta = ""
    if geo:
        geo_meta = ('\n<meta name="geo.region" content="%s">'
                    '\n<meta name="geo.placename" content="%s">'
                    % (esc(geo[0]), esc(geo[1])))
    return """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">{robots}
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{site}{canonical}">
{alts}{geo}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Quietworks">
<meta property="og:locale" content="{locale}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}{img}">
<meta property="og:url" content="{site}{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
<script>try{{var t=localStorage.getItem("qw-theme");if(t)document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}</script>{ld}{extra}
</head>
<body>
""".format(lang=lang, title=esc(title), desc=esc(desc), site=SITE,
           canonical=canonical, alts=hreflang_block(alts), geo=geo_meta,
           locale=BY_CODE[lang]["hreflang"].replace("-", "_"),
           img=og_image or "/assets/img/dashboard-board.png",
           robots=('\n<meta name="robots" content="%s">' % robots) if robots else "",
           ld=ld, extra=extra)


BRAND_SVG = """<svg viewBox="0 0 32 32" aria-hidden="true">
          <rect class="brand-mark-bg" width="32" height="32" rx="7"/>
          <rect class="brand-mark-fg" x="6" y="7"  width="20" height="4" rx="2"/>
          <rect class="brand-mark-fg" x="6" y="14" width="13" height="4" rx="2" opacity=".72"/>
          <rect class="brand-mark-fg" x="6" y="21" width="8"  height="4" rx="2" opacity=".45"/>
        </svg>"""


def lang_picker(lang, targets):
    """The header language menu. `targets` maps every language code to where
    this reader should land - the same page where it exists, that language's
    India hub where it does not. It is a <details>, so it works with
    JavaScript off; initLang() only remembers the choice."""
    s = STR[lang]
    rows = []
    for l in LANGS:
        current = ' aria-current="true"' if l["code"] == lang else ""
        rows.append(
            '          <li><a href="%s" hreflang="%s" lang="%s" data-lang="%s"%s>'
            '<span class="lang-name">%s</span>'
            '<span class="lang-sample">%s</span></a></li>'
            % (targets[l["code"]], l["hreflang"], l["code"], l["code"], current,
               esc(l["endonym"]), esc(l["sample"])))
    return """<details class="lang-pick" data-lang-pick>
        <summary aria-label="{label}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.2"/><path d="M3 12h18M12 2.8c2.4 2.6 3.6 5.7 3.6 9.2s-1.2 6.6-3.6 9.2M12 2.8c-2.4 2.6-3.6 5.7-3.6 9.2s1.2 6.6 3.6 9.2"/></svg>
          <span class="lang-current">{endonym}</span>
        </summary>
        <div class="lang-menu">
          <p class="lang-head">{choose}</p>
          <ul>
{rows}
          </ul>
          <p class="lang-note">{note}</p>
        </div>
      </details>""".format(label=esc(s["n_lang"]), endonym=esc(BY_CODE[lang]["endonym"]),
                           choose=esc(s["n_lang_choose"]), rows="\n".join(rows),
                           note=esc(s["n_lang_note"]))


def header(lang, current, targets):
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    links = [("home", (p + "/") if p else "/", s["n_home"]),
             ("workqueue", p + "/workqueue", s["n_workqueue"]),
             ("pricing", p + "/pricing", s["n_pricing"]),
             ("india", p + "/india", s["n_india"]),
             ("contact", p + "/contact", s["n_contact"])]
    nav = "\n".join(
        '        <a href="%s"%s>%s</a>'
        % (href, ' aria-current="page"' if key == current else "", esc(label))
        for key, href, label in links)
    return """<a class="skip-link" href="#main">{skip}</a>

<header class="site-header">
  <div class="wrap">
    <nav class="nav" aria-label="Main">
      <a class="brand" href="{home}">
        {brand}
        Quietworks
      </a>
      <div class="nav-links" id="nav-links">
{nav}
      </div>
      <div class="nav-actions">
        {picker}
        <button class="theme-toggle" type="button" aria-label="{theme}">
          <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
          <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M19.1 4.9l-1.8 1.8M6.7 17.3l-1.8 1.8"/></svg>
        </button>
        <a class="btn btn-primary btn-sm" href="{contact}?about=trial">{trial}</a>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="{menu}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
        </button>
      </div>
    </nav>
  </div>
</header>

<main id="main">
""".format(skip=esc(s["n_skip"]), home=(p + "/") if p else "/", brand=BRAND_SVG,
           nav=nav, picker=lang_picker(lang, targets), theme=esc(s["n_theme"]),
           contact=p + "/contact", trial=esc(s["n_trial"]), menu=esc(s["n_menu"]))


def footer(lang, wa_msg=None):
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    return """</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-about">
        <a class="brand" href="{home}">
          {brand}
          Quietworks
        </a>
        <p>{about}</p>
      </div>
      <div class="footer-col">
        <h4>{tools}</h4>
        <ul>
          <li><a href="{p}/workqueue">WorkQueue</a></li>
          <li><a href="{p}/workqueue#requirements">{req}</a></li>
          <li><a href="{p}/contact?about=roadmap">{next}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{buying}</h4>
        <ul>
          <li><a href="{p}/pricing">{pricing}</a></li>
          <li><a href="{p}/contact?about=trial">{free}</a></li>
          <li><a href="{p}/contact?about=setup">{setup}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{contact}</h4>
        <ul>
          <li><a href="{p}/india">{states}</a></li>
          <li><a href="mailto:{email}">{email}</a></li>
          <li><a data-whatsapp="{wa}" href="#">WhatsApp</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year>2026</span> {rights}</span>
      <span>{made}</span>
    </div>
  </div>
</footer>

<script src="/assets/js/site.js"></script>
</body>
</html>
""".format(home=(p + "/") if p else "/", brand=BRAND_SVG, p=p,
           about=esc(s["f_about"]), tools=esc(s["f_tools"]),
           req=esc(s["f_requirements"]), next=esc(s["f_next"]),
           buying=esc(s["f_buying"]), pricing=esc(s["n_pricing"]),
           free=esc(s["f_free_trial"]), setup=esc(s["f_setup"]),
           contact=esc(s["f_contact"]), states=esc(s["f_states"]),
           email=EMAIL, wa=esc(wa_msg or s["f_wa_msg"]),
           rights=esc(s["f_rights"]), made=esc(s["f_made"]))


TICK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>')


def trust_row(items):
    return ('<div class="trust-row">\n'
            + "\n".join("          <span>%s %s</span>" % (TICK, esc(i)) for i in items)
            + "\n        </div>")


def check_list(pairs, cls="check-list"):
    """pairs are (bold, rest); either may be empty."""
    rows = []
    for bold, rest in pairs:
        inner = ("<strong>%s</strong> %s" % (esc(bold), esc(rest))).strip() if bold else esc(rest)
        rows.append("          <li>%s</li>" % inner)
    return '<ul class="%s">\n%s\n        </ul>' % (cls, "\n".join(rows))


def faq(pairs, lang):
    rows = []
    for q, a in pairs:
        rows.append("""      <details>
        <summary>%s</summary>
        <div class="faq-body">
          <p>%s</p>
        </div>
      </details>""" % (esc(q), esc(a)))
    return '<div class="faq">\n%s\n    </div>' % "\n".join(rows)


def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in pairs]}


def org_ld():
    return {"@context": "https://schema.org", "@type": "Organization",
            "name": "Quietworks", "url": SITE + "/",
            "logo": SITE + "/assets/img/favicon.svg",
            "email": EMAIL,
            "address": {"@type": "PostalAddress", "addressLocality": "Mumbai",
                        "addressRegion": "Maharashtra", "addressCountry": "IN"},
            "areaServed": {"@type": "Country", "name": "India"}}


def software_ld(lang):
    return {"@context": "https://schema.org", "@type": "SoftwareApplication",
            "name": "WorkQueue", "applicationCategory": "BusinessApplication",
            "operatingSystem": "Windows 10, Windows 11",
            "softwareVersion": "4.0.1",
            "url": SITE + url_for(lang, "workqueue"),
            "inLanguage": [l["hreflang"] for l in LANGS],
            "publisher": {"@type": "Organization", "name": "Quietworks"},
            "offers": {"@type": "Offer", "price": "14999",
                       "priceCurrency": "INR",
                       "url": SITE + url_for(lang, "pricing"),
                       "availability": "https://schema.org/InStock",
                       "eligibleRegion": {"@type": "Country", "name": "India"}}}


# --- 3. The four core pages -------------------------------------------------

def core_targets(page):
    """Where the picker sends a reader from a core page: the same page."""
    return {l["code"]: url_for(l["code"], page) for l in LANGS}


def core_alts(page):
    return {l["code"]: url_for(l["code"], page) for l in LANGS}


def build_home(lang):
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    caps = [(3.2, s["h_film_ch1"], s["h_film_cap1"]),
            (23.4, s["h_film_ch2"], s["h_film_cap2"]),
            (32.4, s["h_film_ch3"], s["h_film_cap3"]),
            (39.6, s["h_film_ch4"], s["h_film_cap4"]),
            (48.6, s["h_film_ch5"], s["h_film_cap5"])]
    stamps = ["0:03", "0:23", "0:32", "0:40", "0:49"]
    chapters = "\n".join(
        '        <li><button type="button" data-film-at="%s" data-film-text="%s">%s <span>%s</span></button></li>'
        % (at, esc(text), esc(label), stamps[i])
        for i, (at, label, text) in enumerate(caps))

    faqs = [(s["h_faq_q%d" % i], s["h_faq_a%d" % i]) for i in range(1, 6)]
    mine = states_for(lang)
    state_links = ""
    if mine:
        state_links = """
    <div class="state-teaser">
      <p>%s</p>
      <div class="chip-row">%s</div>
      <a class="btn btn-ghost btn-sm" href="%s/india">%s</a>
    </div>""" % (esc(s["i_states_p"]),
                 "".join('<a class="chip" href="%s">%s</a>'
                         % (url_for(lang, "state", st["slug"]), esc(st["native"]))
                         for st in mine),
                 p, esc(s["s_other_btn"]))

    body = """
<!-- ===================== Hero ===================== -->
<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">{eyebrow}</span>
        <h1>{h1}</h1>
        <p class="lede">{lede}</p>
        <div class="btn-row">
          <a class="btn btn-primary btn-lg" href="{p}/workqueue">{cta1}</a>
          <a class="btn btn-ghost btn-lg" href="{p}/contact?about=trial">{cta2}</a>
        </div>
        {trust}
      </div>

      <figure style="margin:0">
        <a class="shot-zoom" href="/assets/img/dashboard-board.png" data-zoom
           aria-label="{shot_open}">
          <div class="shot shot-crop">
            <div class="shot-bar">
              <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
              <span class="shot-title">http://192.168.0.10:8420 &mdash; WorkQueue</span>
            </div>
            <img src="/assets/img/dashboard-board.png" width="1920" height="1080"
                 alt="{shot_alt}" fetchpriority="high">
          </div>
        </a>
        <figcaption class="shot-caption">{shot_cap}</figcaption>
      </figure>
    </div>
  </div>
</section>

<!-- ===================== The demo film ===================== -->
<section id="see-it-work">
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">{film_eyebrow}</span>
      <h2>{film_h2}</h2>
      <p class="lede">{film_lede}</p>
    </div>

    <figure class="film" data-film>
      <div class="film-stage">
        <video data-film-video width="1920" height="1080" controls playsinline
               preload="none" poster="/assets/img/demo-poster.jpg"
               aria-describedby="film-caption">
          <source src="/assets/video/workqueue-demo.mp4" type="video/mp4">
          <p class="film-fallback">
            {film_cant}
            <a href="/assets/video/workqueue-demo.mp4">{film_download}</a> (7 MB).
          </p>
        </video>
        <button class="film-play" type="button" data-film-play aria-label="{film_aria}">
          <span class="film-play-mark">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.2v13.6L19 12z"/></svg>
          </span>
          <span class="film-play-text" data-film-label>{film_watch} <b>1:07</b></span>
        </button>
      </div>

      <ol class="film-chapters" data-film-chapters>
{chapters}
      </ol>

      <figcaption class="film-caption" id="film-caption" data-film-caption aria-live="polite">{cap1}</figcaption>

      <p class="film-note">{film_note}</p>
    </figure>
  </div>
</section>

<!-- ===================== The problem ===================== -->
<section class="band">
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">{why_eyebrow}</span>
      <h2>{why_h2}</h2>
      <p class="lede">{why_lede}</p>
    </div>

    <div class="grid grid-3">
      <div class="card reveal">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2 4 5.5V11c0 5 3.4 9.4 8 10.6 4.6-1.2 8-5.6 8-10.6V5.5z"/><path d="m9 12 2 2 4-4"/></svg>
        </div>
        <h3>{why1_h}</h3>
        <p>{why1_p}</p>
      </div>
      <div class="card reveal">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 1v22"/><path d="M17.5 6.5A4 4 0 0 0 14 5h-3.5a3 3 0 0 0 0 6h3a3 3 0 0 1 0 6H9a4 4 0 0 1-3.5-1.5"/></svg>
        </div>
        <h3>{why2_h}</h3>
        <p>{why2_p}</p>
      </div>
      <div class="card reveal">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5a7 7 0 0 1 9.9-6.4"/><path d="M19 11.5a7 7 0 0 1-9.9 6.4"/><path d="M2 2l20 20"/><circle cx="12" cy="12" r="1.6"/></svg>
        </div>
        <h3>{why3_h}</h3>
        <p>{why3_p}</p>
      </div>
    </div>
  </div>
</section>

<!-- ===================== Featured tool ===================== -->
<section>
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">{tool_eyebrow}</span>
      <h2>{tool_h2}</h2>
      <p class="lede">{tool_lede}</p>
    </div>

    <div class="feature-row">
      <div class="feature-text">
        <h3>{f1_h}</h3>
        <p>{f1_p}</p>
        {f1_list}
        <a class="btn btn-ghost" href="{p}/workqueue">{f1_link}</a>
      </div>
      <figure class="strip-stack">
        <div class="shot">
          <img src="/assets/img/bar-strip-left.png" width="500" height="41" alt="{f1_alt_left}">
        </div>
        <div class="shot">
          <img src="/assets/img/bar-strip-chips.png" width="560" height="41" alt="{f1_alt_chips}">
        </div>
        <figcaption class="shot-caption">{f1_cap}</figcaption>
      </figure>
    </div>

    <div class="feature-row reverse">
      <div class="feature-text">
        <h3>{f2_h}</h3>
        <p>{f2_p}</p>
        {f2_list}
        <a class="btn btn-ghost" href="{p}/workqueue#analytics">{f2_link}</a>
      </div>
      <figure style="margin:0">
        <div class="shot shot-crop">
          <div class="shot-bar">
            <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
            <span class="shot-title">WorkQueue &mdash; Analytics</span>
          </div>
          <img src="/assets/img/dashboard-analytics.png" width="1920" height="1080" loading="lazy" alt="{f2_alt}">
        </div>
        <figcaption class="shot-caption">{f2_cap}</figcaption>
      </figure>
    </div>
  </div>
</section>

<!-- ===================== How it works ===================== -->
<section class="band">
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">{start_eyebrow}</span>
      <h2>{start_h2}</h2>
      <p class="lede">{start_lede}</p>
    </div>

    <div class="steps">
      <div class="step reveal"><h3>{s1_h}</h3><p>{s1_p}</p></div>
      <div class="step reveal"><h3>{s2_h}</h3><p>{s2_p}</p></div>
      <div class="step reveal"><h3>{s3_h}</h3><p>{s3_p}</p></div>
    </div>{state_links}
  </div>
</section>

<!-- ===================== FAQ ===================== -->
<section>
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">{faq_eyebrow}</span>
      <h2>{faq_h2}</h2>
    </div>
    {faq}
  </div>
</section>

<!-- ===================== CTA ===================== -->
<section class="band cta-band">
  <div class="wrap">
    <h2>{cta_h2}</h2>
    <p class="lede">{cta_p}</p>
    <div class="btn-row center">
      <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta_b1}</a>
      <a class="btn btn-ghost btn-lg" href="{p}/pricing">{cta_b2}</a>
    </div>
  </div>
</section>
""".format(p=p, eyebrow=esc(s["h_eyebrow"]), h1=esc(s["h_h1"]), lede=esc(s["h_lede"]),
           cta1=esc(s["h_cta1"]), cta2=esc(s["h_cta2"]),
           trust=trust_row([s["h_trust1"], s["h_trust2"], s["h_trust3"]]),
           shot_open=esc(s["h_shot_open"]), shot_alt=esc(s["h_shot_alt"]),
           shot_cap=esc(s["h_shot_cap"]),
           film_eyebrow=esc(s["h_film_eyebrow"]), film_h2=esc(s["h_film_h2"]),
           film_lede=esc(s["h_film_lede"]), film_cant=esc(s["h_film_cant"]),
           film_download=esc(s["h_film_download"]), film_aria=esc(s["h_film_aria"]),
           film_watch=esc(s["h_film_watch"]), chapters=chapters,
           cap1=esc(s["h_film_cap1"]), film_note=esc(s["h_film_note"]),
           why_eyebrow=esc(s["h_why_eyebrow"]), why_h2=esc(s["h_why_h2"]),
           why_lede=esc(s["h_why_lede"]),
           why1_h=esc(s["h_why1_h"]), why1_p=esc(s["h_why1_p"]),
           why2_h=esc(s["h_why2_h"]), why2_p=esc(s["h_why2_p"]),
           why3_h=esc(s["h_why3_h"]), why3_p=esc(s["h_why3_p"]),
           tool_eyebrow=esc(s["h_tool_eyebrow"]), tool_h2=esc(s["h_tool_h2"]),
           tool_lede=esc(s["h_tool_lede"]),
           f1_h=esc(s["h_f1_h"]), f1_p=esc(s["h_f1_p"]),
           f1_list=check_list([(s["h_f1_l1_b"], s["h_f1_l1"]),
                               (s["h_f1_l2_b"], s["h_f1_l2"]),
                               (s["h_f1_l3_b"], s["h_f1_l3"])]),
           f1_link=esc(s["h_f1_link"]), f1_alt_left=esc(s["h_f1_alt_left"]),
           f1_alt_chips=esc(s["h_f1_alt_chips"]), f1_cap=esc(s["h_f1_cap"]),
           f2_h=esc(s["h_f2_h"]), f2_p=esc(s["h_f2_p"]),
           f2_list=check_list([(s["h_f2_l1_b"], s["h_f2_l1"]),
                               (s["h_f2_l2_b"], s["h_f2_l2"]),
                               (s["h_f2_l3_b"], s["h_f2_l3"])]),
           f2_link=esc(s["h_f2_link"]), f2_alt=esc(s["h_f2_alt"]), f2_cap=esc(s["h_f2_cap"]),
           start_eyebrow=esc(s["h_start_eyebrow"]), start_h2=esc(s["h_start_h2"]),
           start_lede=esc(s["h_start_lede"]),
           s1_h=esc(s["h_s1_h"]), s1_p=esc(s["h_s1_p"]),
           s2_h=esc(s["h_s2_h"]), s2_p=esc(s["h_s2_p"]),
           s3_h=esc(s["h_s3_h"]), s3_p=esc(s["h_s3_p"]), state_links=state_links,
           faq_eyebrow=esc(s["h_faq_eyebrow"]), faq_h2=esc(s["h_faq_h2"]),
           faq=faq(faqs, lang), cta_h2=esc(s["h_cta_h2"]), cta_p=esc(s["h_cta_p"]),
           cta_b1=esc(s["h_cta_b1"]), cta_b2=esc(s["h_cta_b2"]))

    ld = {"@context": "https://schema.org", "@graph": [
        org_ld(), software_ld(lang),
        {"@type": "WebSite", "name": "Quietworks", "url": SITE + "/",
         "inLanguage": [l["hreflang"] for l in LANGS]},
        faq_ld(faqs)]}
    for node in ld["@graph"]:
        node.pop("@context", None)
    return (head(lang, s["h_title"], s["h_desc"], url_for(lang, "home"),
                 core_alts("home"), jsonld=ld)
            + header(lang, "home", core_targets("home")) + body + footer(lang))


def build_workqueue(lang):
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    faqs = [(s["w_faq_q%d" % i], s["w_faq_a%d" % i]) for i in range(1, 7)]
    body = """
<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">{eyebrow}</span>
        <h1>{h1}</h1>
        <p class="lede">{lede}</p>
        <div class="btn-row">
          <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta1}</a>
          <a class="btn btn-ghost btn-lg" href="{p}/pricing">{cta2}</a>
        </div>
        {trust}
      </div>
      <figure style="margin:0">
        <div class="shot shot-crop">
          <div class="shot-bar">
            <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
            <span class="shot-title">http://192.168.0.10:8420 &mdash; WorkQueue</span>
          </div>
          <img src="/assets/img/dashboard-board.png" width="1920" height="1080"
               alt="{hero_alt}" fetchpriority="high">
        </div>
        <figcaption class="shot-caption">{hero_cap}</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">{strip_eyebrow}</span>
      <h2>{strip_h2}</h2>
      <p class="lede">{strip_lede}</p>
    </div>

    <figure class="strip-actual">
      <img src="/assets/img/bar-strip.png" width="1920" height="41" loading="lazy" alt="{strip_alt}">
      <figcaption class="shot-caption">{strip_cap}</figcaption>
    </figure>

    <div class="strip-zoom">
      <figure>
        <div class="shot">
          <img src="/assets/img/bar-strip-left.png" width="500" height="41" loading="lazy" alt="{f1_alt_left}">
        </div>
        <figcaption class="shot-caption"><strong>{left_b}</strong> {left}</figcaption>
      </figure>
      <figure>
        <div class="shot">
          <img src="/assets/img/bar-strip-chips.png" width="560" height="41" loading="lazy" alt="{f1_alt_chips}">
        </div>
        <figcaption class="shot-caption"><strong>{right_b}</strong> {right}</figcaption>
      </figure>
    </div>

    <figure style="margin:0 0 clamp(30px,5vw,52px)">
      <div class="shot" style="max-width:860px;margin-inline:auto">
        <img src="/assets/img/bar-panel.png" width="822" height="278" loading="lazy" alt="{panel_alt}">
      </div>
      <figcaption class="shot-caption center">{panel_cap}</figcaption>
    </figure>

    <div class="grid grid-3">
      <div class="card reveal"><h3>{c1_h}</h3><p>{c1_p}</p></div>
      <div class="card reveal"><h3>{c2_h}</h3><p>{c2_p}</p></div>
      <div class="card reveal"><h3>{c3_h}</h3><p>{c3_p}</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="feature-row">
      <div class="feature-text">
        <span class="eyebrow">{board_eyebrow}</span>
        <h3>{board_h3}</h3>
        <p>{board_p}</p>
        {board_list}
      </div>
      <figure style="margin:0">
        <div class="shot shot-crop">
          <div class="shot-bar">
            <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
            <span class="shot-title">WorkQueue &mdash; Board</span>
          </div>
          <img src="/assets/img/dashboard-board.png" width="1920" height="1080" loading="lazy" alt="{board_alt}">
        </div>
      </figure>
    </div>

    <div class="feature-row reverse" id="analytics">
      <div class="feature-text">
        <span class="eyebrow">{an_eyebrow}</span>
        <h3>{an_h3}</h3>
        <p>{an_p}</p>
        {an_list}
      </div>
      <figure style="margin:0">
        <div class="shot shot-crop">
          <div class="shot-bar">
            <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
            <span class="shot-title">WorkQueue &mdash; Analytics</span>
          </div>
          <img src="/assets/img/dashboard-analytics.png" width="1920" height="1080" loading="lazy" alt="{an_alt}">
        </div>
        <figcaption class="shot-caption">{an_cap}</figcaption>
      </figure>
    </div>

    <div class="feature-row">
      <div class="feature-text">
        <span class="eyebrow">{hist_eyebrow}</span>
        <h3>{hist_h3}</h3>
        <p>{hist_p}</p>
        {hist_list}
      </div>
      <figure style="margin:0">
        <div class="shot shot-crop">
          <div class="shot-bar">
            <span class="shot-dot"></span><span class="shot-dot"></span><span class="shot-dot"></span>
            <span class="shot-title">WorkQueue &mdash; Calendar</span>
          </div>
          <img src="/assets/img/dashboard-calendar.png" width="1920" height="1080" loading="lazy" alt="{hist_alt}">
        </div>
      </figure>
    </div>
  </div>
</section>

<section class="band-ink">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">{res_eyebrow}</span>
      <h2>{res_h2}</h2>
      <p class="lede">{res_lede}</p>
    </div>
    <div class="grid grid-2">
      <div>{res_a}</div>
      <div>{res_b}</div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">{arch_eyebrow}</span>
      <h2>{arch_h2}</h2>
      <p class="lede">{arch_lede}</p>
    </div>

    <div class="diagram">
      <svg viewBox="0 0 860 300" role="img" aria-labelledby="diagram-title diagram-desc">
        <title id="diagram-title">{dtitle}</title>
        <desc id="diagram-desc">{ddesc}</desc>
        <rect x="6" y="6" width="848" height="256" rx="14" fill="none" stroke="currentColor" stroke-opacity=".18" stroke-width="1.5" stroke-dasharray="7 6"/>
        <path class="dg-line" d="M268 145 C 400 145, 440 60, 592 60"/>
        <path class="dg-line" d="M268 145 H 592"/>
        <path class="dg-line" d="M268 145 C 400 145, 440 230, 592 230"/>
        <rect class="dg-box-a" x="16" y="85" width="252" height="122" rx="11"/>
        <text class="dg-t" x="38" y="116">{manager}</text>
        <text class="dg-s" x="38" y="140">{m1}</text>
        <text class="dg-s" x="38" y="161">{m2}</text>
        <text class="dg-s" x="38" y="182">{m3}</text>
        <rect class="dg-box" x="592" y="30" width="252" height="60" rx="11"/>
        <text class="dg-t" x="612" y="55">{employee}</text>
        <text class="dg-s" x="612" y="75">{e1}</text>
        <rect class="dg-box" x="592" y="115" width="252" height="60" rx="11"/>
        <text class="dg-t" x="612" y="140">{employee}</text>
        <text class="dg-s" x="612" y="160">{e1}</text>
        <rect class="dg-box" x="592" y="200" width="252" height="60" rx="11"/>
        <text class="dg-t" x="612" y="225">{employee}</text>
        <text class="dg-s" x="612" y="245">{e1}</text>
        <text class="dg-l" x="430" y="132" text-anchor="middle">{http}</text>
        <text class="dg-l" x="430" y="172" text-anchor="middle">{udp}</text>
        <text class="dg-s" x="430" y="285" text-anchor="middle">{inside}</text>
      </svg>
    </div>

    <div class="grid grid-2" style="margin-top:36px">
      <div class="card"><h3>{ac1_h}</h3><p>{ac1_p}</p></div>
      <div class="card"><h3>{ac2_h}</h3><p>{ac2_p}</p></div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">{cel_eyebrow}</span>
      <h2>{cel_h2}</h2>
      <p class="lede">{cel_lede}</p>
      <p class="small muted">{cel_note}</p>
    </div>
  </div>
</section>

<section id="requirements">
  <div class="wrap wrap-narrow">
    <div class="section-head">
      <span class="eyebrow">{req_eyebrow}</span>
      <h2>{req_h2}</h2>
    </div>
    <dl class="spec-list">
{req_rows}
    </dl>

    <h3 style="margin-top:48px">{not_h3}</h3>
    <p class="muted">{not_p}</p>
    {not_list}
  </div>
</section>

<section class="band">
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">{faq_eyebrow}</span>
      <h2>{faq_h2}</h2>
    </div>
    {faq}
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>{cta_h2}</h2>
    <p class="lede">{cta_p}</p>
    <div class="btn-row center">
      <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta_b1}</a>
      <a class="btn btn-ghost btn-lg" href="{p}/pricing">{cta_b2}</a>
    </div>
  </div>
</section>
""".format(p=p, eyebrow=esc(s["w_eyebrow"]), h1=esc(s["w_h1"]), lede=esc(s["w_lede"]),
           cta1=esc(s["h_cta_b1"]), cta2=esc(s["h_cta_b2"]),
           trust=trust_row([s["w_trust1"], s["w_trust2"], s["w_trust3"]]),
           hero_alt=esc(s["w_hero_alt"]), hero_cap=esc(s["w_hero_cap"]),
           strip_eyebrow=esc(s["w_strip_eyebrow"]), strip_h2=esc(s["w_strip_h2"]),
           strip_lede=esc(s["w_strip_lede"]), strip_alt=esc(s["w_strip_alt"]),
           strip_cap=esc(s["w_strip_cap"]),
           f1_alt_left=esc(s["h_f1_alt_left"]), f1_alt_chips=esc(s["h_f1_alt_chips"]),
           left_b=esc(s["w_strip_left_b"]), left=esc(s["w_strip_left"]),
           right_b=esc(s["w_strip_right_b"]), right=esc(s["w_strip_right"]),
           panel_alt=esc(s["w_panel_alt"]), panel_cap=esc(s["w_panel_cap"]),
           c1_h=esc(s["w_c1_h"]), c1_p=esc(s["w_c1_p"]),
           c2_h=esc(s["w_c2_h"]), c2_p=esc(s["w_c2_p"]),
           c3_h=esc(s["w_c3_h"]), c3_p=esc(s["w_c3_p"]),
           board_eyebrow=esc(s["w_board_eyebrow"]), board_h3=esc(s["w_board_h3"]),
           board_p=esc(s["w_board_p"]), board_alt=esc(s["w_board_alt"]),
           board_list=check_list([(s["w_board_l%d_b" % i], s["w_board_l%d" % i])
                                  for i in range(1, 5)]),
           an_eyebrow=esc(s["w_an_eyebrow"]), an_h3=esc(s["w_an_h3"]),
           an_p=esc(s["w_an_p"]), an_alt=esc(s["w_an_alt"]), an_cap=esc(s["w_an_cap"]),
           an_list=check_list([(s["w_an_l%d_b" % i], s["w_an_l%d" % i])
                               for i in range(1, 6)]),
           hist_eyebrow=esc(s["w_hist_eyebrow"]), hist_h3=esc(s["w_hist_h3"]),
           hist_p=esc(s["w_hist_p"]), hist_alt=esc(s["w_hist_alt"]),
           hist_list=check_list([(s["w_hist_l%d_b" % i], s["w_hist_l%d" % i])
                                 for i in range(1, 4)]),
           res_eyebrow=esc(s["w_res_eyebrow"]), res_h2=esc(s["w_res_h2"]),
           res_lede=esc(s["w_res_lede"]),
           res_a=check_list([(s["w_res_l1_b"], s["w_res_l1"]),
                             (s["w_res_l2_b"], s["w_res_l2"])]),
           res_b=check_list([(s["w_res_l3_b"], s["w_res_l3"]),
                             (s["w_res_l4_b"], s["w_res_l4"])]),
           arch_eyebrow=esc(s["w_arch_eyebrow"]), arch_h2=esc(s["w_arch_h2"]),
           arch_lede=esc(s["w_arch_lede"]), dtitle=esc(s["w_arch_dtitle"]),
           ddesc=esc(s["w_arch_ddesc"]), manager=esc(s["w_arch_manager"]),
           m1=esc(s["w_arch_m1"]), m2=esc(s["w_arch_m2"]), m3=esc(s["w_arch_m3"]),
           employee=esc(s["w_arch_employee"]), e1=esc(s["w_arch_e1"]),
           http=esc(s["w_arch_http"]), udp=esc(s["w_arch_udp"]),
           inside=esc(s["w_arch_inside"]),
           ac1_h=esc(s["w_arch_c1_h"]), ac1_p=esc(s["w_arch_c1_p"]),
           ac2_h=esc(s["w_arch_c2_h"]), ac2_p=esc(s["w_arch_c2_p"]),
           cel_eyebrow=esc(s["w_cel_eyebrow"]), cel_h2=esc(s["w_cel_h2"]),
           cel_lede=esc(s["w_cel_lede"]), cel_note=esc(s["w_cel_note"]),
           req_eyebrow=esc(s["w_req_eyebrow"]), req_h2=esc(s["w_req_h2"]),
           req_rows="\n".join(
               "      <div><dt>%s</dt><dd>%s</dd></div>"
               % (esc(s["w_req_d%dt" % i]), esc(s["w_req_d%dd" % i]))
               for i in range(1, 7)),
           not_h3=esc(s["w_not_h3"]), not_p=esc(s["w_not_p"]),
           not_list=check_list([(s["w_not_l%d_b" % i], s["w_not_l%d" % i])
                                for i in range(1, 6)]),
           faq_eyebrow=esc(s["w_faq_eyebrow"]), faq_h2=esc(s["w_faq_h2"]),
           faq=faq(faqs, lang), cta_h2=esc(s["w_cta_h2"]), cta_p=esc(s["w_cta_p"]),
           cta_b1=esc(s["h_cta_b1"]), cta_b2=esc(s["h_cta_b2"]))

    ld = {"@context": "https://schema.org", "@graph": [software_ld(lang), faq_ld(faqs)]}
    for node in ld["@graph"]:
        node.pop("@context", None)
    return (head(lang, s["w_title"], s["w_desc"], url_for(lang, "workqueue"),
                 core_alts("workqueue"), jsonld=ld)
            + header(lang, "workqueue", core_targets("workqueue")) + body
            + footer(lang))


def build_pricing(lang):
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    faqs = [(s["p_faq_q%d" % i], s["p_faq_a%d" % i]) for i in range(1, 6)]
    rows = [(s["p_cmp_r1"], "1,08,000", "93,001"),
            (s["p_cmp_r2"], "2,16,000", "2,01,001"),
            (s["p_cmp_r3"], "5,40,000", "5,25,001")]
    table_rows = "\n".join("""          <tr>
            <th scope="row">%s</th>
            <td><strong>&#8377;14,999</strong> <span class="muted small">%s</span></td>
            <td>&#8377;%s</td>
            <td class="yes">&#8377;%s %s</td>
          </tr>""" % (esc(label), esc(s["p_cmp_once"]), rent, kept, esc(s["p_cmp_kept"]))
                           for label, rent, kept in rows)

    body = """
<section class="hero">
  <div class="wrap wrap-narrow center">
    <span class="eyebrow">{eyebrow}</span>
    <h1 style="max-width:none">{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="price-grid">
      <div class="price-card">
        <h3>{trial_h}</h3>
        <p class="price-tagline">{trial_tag}</p>
        <div class="price-amount"><span class="amt">{trial_amt}</span><span class="per">{trial_per}</span></div>
        <p class="price-alt">{trial_alt}</p>
        <a class="btn btn-ghost" href="{p}/contact?about=trial">{trial_btn}</a>
        {trial_list}
      </div>

      <div class="price-card featured">
        <span class="price-badge">{lic_badge}</span>
        <h3>{lic_h}</h3>
        <p class="price-tagline">{lic_tag}</p>
        <div class="price-amount"><span class="amt">&#8377;14,999</span><span class="per">{lic_per}</span></div>
        <p class="price-alt">{lic_alt}</p>
        <a class="btn btn-primary" href="{p}/contact?about=licence">{lic_btn}</a>
        {lic_list}
      </div>

      <div class="price-card">
        <h3>{set_h}</h3>
        <p class="price-tagline">{set_tag}</p>
        <div class="price-amount"><span class="amt">&#8377;7,500</span><span class="per">{set_per}</span></div>
        <p class="price-alt">{set_alt}</p>
        <a class="btn btn-ghost" href="{p}/contact?about=setup">{set_btn}</a>
        {set_list}
      </div>
    </div>

    <div class="callout" style="margin-top:40px">
      <p><strong>{after_b}</strong> {after}</p>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">{cmp_eyebrow}</span>
      <h2>{cmp_h2}</h2>
      <p class="lede">{cmp_lede}</p>
    </div>
    <div class="table-scroll">
      <table>
        <caption class="visually-hidden">{cmp_caption}</caption>
        <thead>
          <tr>
            <th scope="col">{th1}</th>
            <th scope="col">{th2}</th>
            <th scope="col">{th3}</th>
            <th scope="col">{th4}</th>
          </tr>
        </thead>
        <tbody>
{table_rows}
        </tbody>
      </table>
    </div>
    <p class="small muted" style="margin-top:14px">{cmp_note}</p>
  </div>
</section>

<section>
  <div class="wrap wrap-narrow">
    <div class="section-head">
      <span class="eyebrow">{inc_eyebrow}</span>
      <h2>{inc_h2}</h2>
    </div>
    <dl class="spec-list">
{inc_rows}
    </dl>
  </div>
</section>

<section class="band">
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">{faq_eyebrow}</span>
      <h2>{faq_h2}</h2>
    </div>
    {faq}
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>{cta_h2}</h2>
    <p class="lede">{cta_p}</p>
    <div class="btn-row center">
      <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta_b1}</a>
      <a class="btn btn-ghost btn-lg" href="{p}/workqueue">{cta_b2}</a>
    </div>
  </div>
</section>
""".format(p=p, eyebrow=esc(s["p_eyebrow"]), h1=esc(s["p_h1"]), lede=esc(s["p_lede"]),
           trial_h=esc(s["p_trial_h"]), trial_tag=esc(s["p_trial_tag"]),
           trial_amt=esc(s["p_trial_amt"]), trial_per=esc(s["p_trial_per"]),
           trial_alt=esc(s["p_trial_alt"]), trial_btn=esc(s["p_trial_btn"]),
           trial_list=check_list([("", s["p_trial_l%d" % i]) for i in range(1, 5)]),
           lic_badge=esc(s["p_lic_badge"]), lic_h=esc(s["p_lic_h"]),
           lic_tag=esc(s["p_lic_tag"]), lic_per=esc(s["p_lic_per"]),
           lic_alt=esc(s["p_lic_alt"]), lic_btn=esc(s["p_lic_btn"]),
           lic_list=check_list([(s["p_lic_l1_b"], s["p_lic_l1"]),
                                (s["p_lic_l2_b"], s["p_lic_l2"]),
                                (s["p_lic_l3_b"], s["p_lic_l3"]),
                                ("", s["p_lic_l4"]), ("", s["p_lic_l5"])]),
           set_h=esc(s["p_set_h"]), set_tag=esc(s["p_set_tag"]),
           set_per=esc(s["p_set_per"]), set_alt=esc(s["p_set_alt"]),
           set_btn=esc(s["p_set_btn"]),
           set_list=check_list([("", s["p_set_l%d" % i]) for i in range(1, 5)]),
           after_b=esc(s["p_after_b"]), after=esc(s["p_after"]),
           cmp_eyebrow=esc(s["p_cmp_eyebrow"]), cmp_h2=esc(s["p_cmp_h2"]),
           cmp_lede=esc(s["p_cmp_lede"]), cmp_caption=esc(s["p_cmp_caption"]),
           th1=esc(s["p_cmp_th1"]), th2=esc(s["p_cmp_th2"]),
           th3=esc(s["p_cmp_th3"]), th4=esc(s["p_cmp_th4"]),
           table_rows=table_rows, cmp_note=esc(s["p_cmp_note"]),
           inc_eyebrow=esc(s["p_inc_eyebrow"]), inc_h2=esc(s["p_inc_h2"]),
           inc_rows="\n".join(
               "      <div><dt>%s</dt><dd>%s</dd></div>"
               % (esc(s["p_inc_d%dt" % i]), esc(s["p_inc_d%dd" % i]))
               for i in range(1, 7)),
           faq_eyebrow=esc(s["p_faq_eyebrow"]), faq_h2=esc(s["p_faq_h2"]),
           faq=faq(faqs, lang), cta_h2=esc(s["p_cta_h2"]), cta_p=esc(s["p_cta_p"]),
           cta_b1=esc(s["h_cta_b1"]), cta_b2=esc(s["p_cta_b2"]))

    ld = {"@context": "https://schema.org", "@graph": [software_ld(lang), faq_ld(faqs)]}
    for node in ld["@graph"]:
        node.pop("@context", None)
    return (head(lang, s["p_title"], s["p_desc"], url_for(lang, "pricing"),
                 core_alts("pricing"), jsonld=ld)
            + header(lang, "pricing", core_targets("pricing")) + body + footer(lang))


def build_contact(lang):
    s = STR[lang]
    sizes = "\n".join('                <option%s>%s</option>'
                      % (' value=""' if i == 0 else "", esc(s["c_o_size%d" % i]))
                      for i in range(5))
    enquiry = "\n".join('              <option value="%s">%s</option>'
                        % (v, esc(s["c_o_%s" % v]))
                        for v in ("trial", "licence", "setup", "custom",
                                  "roadmap", "other"))
    body = """
<section class="hero">
  <div class="wrap">
    <div class="contact-grid">
      <div>
        <span class="eyebrow">{eyebrow}</span>
        <h1 style="max-width:18ch">{h1}</h1>
        <p class="lede">{lede}</p>

        <div style="margin-top:32px">
          <div class="channel">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 6.5 9 6 9-6"/></svg>
            <div>
              <div class="channel-label">{email_l}</div>
              <a href="mailto:{email}">{email}</a>
              <p class="small">{email_p}</p>
            </div>
          </div>
          <div class="channel">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21l1.7-5A8.4 8.4 0 1 1 8 19.3z"/><path d="M8.6 9.4c.3 2.6 3.4 5.7 6 6l1.2-1.6 2 1-.4 1.6c-2.6.9-7.7-2.6-9-6.4l1.5-.8z" fill="currentColor" stroke="none"/></svg>
            <div>
              <div class="channel-label">{wa_l}</div>
              <a data-whatsapp="{wa_msg}" href="#">{wa_link}</a>
              <p class="small">{wa_p}</p>
            </div>
          </div>
          <div class="channel">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.2"/><path d="M12 7.5v5l3 2"/></svg>
            <div>
              <div class="channel-label">{hours_l}</div>
              <span class="muted">{hours_v}</span>
              <p class="small">{hours_p}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="padding:clamp(24px,4vw,36px)">
        <h2 style="font-size:23px">{form_h}</h2>
        <p class="small muted" style="margin-bottom:24px">{form_p}</p>

        <form class="form-grid" data-contact-form novalidate>
          <input class="hp" type="text" name="botcheck" tabindex="-1" autocomplete="off" aria-hidden="true">

          <div class="field">
            <label for="f-name">{f_name}</label>
            <input id="f-name" name="name" type="text" autocomplete="name" required>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="f-email">{f_email}</label>
              <input id="f-email" name="email" type="email" autocomplete="email" required>
            </div>
            <div class="field">
              <label for="f-phone">{f_phone} <span class="hint">{optional}</span></label>
              <input id="f-phone" name="phone" type="tel" autocomplete="tel">
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="f-company">{f_company} <span class="hint">{optional}</span></label>
              <input id="f-company" name="company" type="text" autocomplete="organization">
            </div>
            <div class="field">
              <label for="f-size">{f_size} <span class="hint">{optional}</span></label>
              <select id="f-size" name="team_size">
{sizes}
              </select>
            </div>
          </div>

          <div class="field">
            <label for="f-enquiry">{f_enquiry}</label>
            <select id="f-enquiry" name="enquiry" required>
{enquiry}
            </select>
          </div>

          <div class="field">
            <label for="f-message">{f_message} <span class="hint">{optional}</span></label>
            <textarea id="f-message" name="message" placeholder="{placeholder}"></textarea>
          </div>

          <div class="form-status" hidden role="status" aria-live="polite"></div>

          <button class="btn btn-primary btn-lg" type="submit">{f_send}</button>

          <p class="small muted" style="margin:0">{privacy}</p>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <span class="eyebrow">{next_eyebrow}</span>
      <h2>{next_h2}</h2>
    </div>
    <div class="steps">
      <div class="step"><h3>{n1_h}</h3><p>{n1_p}</p></div>
      <div class="step"><h3>{n2_h}</h3><p>{n2_p}</p></div>
      <div class="step"><h3>{n3_h}</h3><p>{n3_p}</p></div>
    </div>
  </div>
</section>
""".format(eyebrow=esc(s["c_eyebrow"]), h1=esc(s["c_h1"]), lede=esc(s["c_lede"]),
           email=EMAIL, email_l=esc(s["c_email_l"]), email_p=esc(s["c_email_p"]),
           wa_l=esc(s["c_wa_l"]), wa_link=esc(s["c_wa_link"]), wa_p=esc(s["c_wa_p"]),
           wa_msg=esc(s["f_wa_msg"]),
           hours_l=esc(s["c_hours_l"]), hours_v=esc(s["c_hours_v"]),
           hours_p=esc(s["c_hours_p"]),
           form_h=esc(s["c_form_h"]), form_p=esc(s["c_form_p"]),
           f_name=esc(s["c_f_name"]), f_email=esc(s["c_f_email"]),
           f_phone=esc(s["c_f_phone"]), f_company=esc(s["c_f_company"]),
           f_size=esc(s["c_f_size"]), f_enquiry=esc(s["c_f_enquiry"]),
           f_message=esc(s["c_f_message"]), optional=esc(s["c_f_optional"]),
           f_send=esc(s["c_f_send"]), placeholder=esc(s["c_f_placeholder"]),
           privacy=esc(s["c_f_privacy"]), sizes=sizes, enquiry=enquiry,
           next_eyebrow=esc(s["c_next_eyebrow"]), next_h2=esc(s["c_next_h2"]),
           n1_h=esc(s["c_n1_h"]), n1_p=esc(s["c_n1_p"]),
           n2_h=esc(s["c_n2_h"]), n2_p=esc(s["c_n2_p"]),
           n3_h=esc(s["c_n3_h"]), n3_p=esc(s["c_n3_p"]))

    ld = {"@context": "https://schema.org", "@type": "ContactPage",
          "url": SITE + url_for(lang, "contact"),
          "mainEntity": {"@type": "Organization", "name": "Quietworks",
                         "email": EMAIL,
                         "contactPoint": {"@type": "ContactPoint",
                                          "contactType": "sales",
                                          "email": EMAIL,
                                          "areaServed": "IN",
                                          "availableLanguage":
                                              [l["english"] for l in LANGS]}}}
    return (head(lang, s["c_title"], s["c_desc"], url_for(lang, "contact"),
                 core_alts("contact"), jsonld=ld)
            + header(lang, "contact", core_targets("contact")) + body + footer(lang))


# --- 4. The India hub and the per-state pages -------------------------------

def build_india(lang):
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    states = [st for st in STATES if st["slug"] not in UT_SLUGS]
    uts = [st for st in STATES if st["slug"] in UT_SLUGS]

    def group(items):
        """A state's page exists in English and, where the two differ, in that
        state's own language - not in all twelve. Send a reader to the version
        that is actually there: their own language when this is their state,
        English otherwise, because English is the one they can certainly read."""
        rows = []
        for st in items:
            if st["lang"] == lang:
                href, tag = url_for(lang, "state", st["slug"]), ""
            else:
                href = url_for("en", "state", st["slug"])
                tag = ' hreflang="en-IN" lang="en"' if lang != "en" else ""
            native = st["native"] if st["lang"] != "en" else ""
            sub = ('<span class="state-native" lang="%s">%s</span>'
                   % (st["lang"], esc(native))) if native else ""
            rows.append(
                '        <li><a href="%s"%s><span class="state-name">%s</span>%s'
                '<span class="state-cities">%s</span></a></li>'
                % (href, tag, esc(st["name"]), sub,
                   esc(", ".join(st["cities"][:3]))))
        return "\n".join(rows)

    lang_cards = "\n".join(
        '        <li><a href="%s" hreflang="%s" lang="%s"><span class="lang-name">%s</span>'
        '<span class="lang-sample">%s</span></a></li>'
        % (url_for(l["code"], "home"), l["hreflang"], l["code"],
           esc(l["endonym"]), esc(l["sample"]))
        for l in LANGS)

    body = """
<section class="hero">
  <div class="wrap wrap-narrow center">
    <span class="eyebrow">{eyebrow}</span>
    <h1 style="max-width:none">{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="section-head">
      <h2>{states_h2}</h2>
      <p class="lede">{states_p}</p>
    </div>

    <h3 class="group-head">{group_states}</h3>
    <ul class="state-grid">
{states_rows}
    </ul>

    <h3 class="group-head">{group_uts}</h3>
    <ul class="state-grid">
{ut_rows}
    </ul>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head center">
      <h2>{why_h2}</h2>
    </div>
    <div class="grid grid-2">
      <div class="card"><h3>{w1_h}</h3><p>{w1_p}</p></div>
      <div class="card"><h3>{w2_h}</h3><p>{w2_p}</p></div>
      <div class="card"><h3>{w3_h}</h3><p>{w3_p}</p></div>
      <div class="card"><h3>{w4_h}</h3><p>{w4_p}</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap wrap-narrow">
    <div class="section-head center">
      <h2>{langs_h2}</h2>
      <p class="lede">{langs_p}</p>
    </div>
    <ul class="lang-grid">
{lang_cards}
    </ul>
  </div>
</section>

<section class="band cta-band">
  <div class="wrap">
    <h2>{cta_h2}</h2>
    <p class="lede">{cta_p}</p>
    <div class="btn-row center">
      <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta_b1}</a>
      <a class="btn btn-ghost btn-lg" href="{p}/pricing">{cta_b2}</a>
    </div>
  </div>
</section>
""".format(p=p, eyebrow=esc(s["i_eyebrow"]), h1=esc(s["i_h1"]), lede=esc(s["i_lede"]),
           states_h2=esc(s["i_states_h2"]), states_p=esc(s["i_states_p"]),
           group_states=esc(s["i_group_states"]), states_rows=group(states),
           group_uts=esc(s["i_group_uts"]), ut_rows=group(uts),
           why_h2=esc(s["i_why_h2"]),
           w1_h=esc(s["i_why1_h"]), w1_p=esc(s["i_why1_p"]),
           w2_h=esc(s["i_why2_h"]), w2_p=esc(s["i_why2_p"]),
           w3_h=esc(s["i_why3_h"]), w3_p=esc(s["i_why3_p"]),
           w4_h=esc(s["i_why4_h"]), w4_p=esc(s["i_why4_p"]),
           langs_h2=esc(s["i_langs_h2"]), langs_p=esc(s["i_langs_p"]),
           lang_cards=lang_cards,
           cta_h2=esc(s["h_cta_h2"]), cta_p=esc(s["h_cta_p"]),
           cta_b1=esc(s["h_cta_b1"]), cta_b2=esc(s["h_cta_b2"]))

    ld = {"@context": "https://schema.org", "@type": "CollectionPage",
          "name": s["i_title"], "url": SITE + url_for(lang, "india"),
          "about": {"@type": "Country", "name": "India"},
          "hasPart": [{"@type": "WebPage", "name": st["name"],
                       "url": SITE + url_for(lang, "state", st["slug"])}
                      for st in STATES]}
    return (head(lang, s["i_title"], s["i_desc"], url_for(lang, "india"),
                 core_alts("india"), jsonld=ld)
            + header(lang, "india", core_targets("india")) + body + footer(lang))


UT_SLUGS = {"andaman-and-nicobar-islands", "chandigarh",
            "dadra-and-nagar-haveli-and-daman-and-diu", "delhi",
            "jammu-and-kashmir", "ladakh", "lakshadweep", "puducherry"}


def state_title(lang, values):
    """The state title, with the tagline dropped when the state's name is long
    enough on its own to push the whole thing past what a result page shows.
    "Dadra and Nagar Haveli and Daman and Diu" is 40 characters before the
    sentence even starts."""
    title = fmt(lang, "s_title", values)
    if len(title) > 72 and "—" in title:
        return title.split("—")[0].strip()
    return title


def build_state(st, lang):
    """One state page. `lang` is either "en" or that state's own language."""
    s = STR[lang]
    p = "" if lang == "en" else "/" + lang
    native = lang != "en"
    name = st["native"] if native else st["name"]
    cities = st["cities_native"] if native else st["cities"]
    trade = st["trade_native"] if native else st["trade"]
    hub = cities[0]
    other = BY_CODE[st["lang"]]["endonym"] if st["lang"] != "en" else None

    v = dict(state=name, hub=hub, cities=", ".join(cities), trade=trade,
             lang=other or "")

    # The cross-language button, only where a second version of this page
    # actually exists.
    swap = ""
    if st["lang"] != "en":
        if native:
            swap = ('<a class="btn btn-ghost" href="%s">%s</a>'
                    % (url_for("en", "state", st["slug"]), esc(s["s_en_btn"])))
        else:
            swap = ('<a class="btn btn-ghost" href="%s" hreflang="%s" lang="%s">%s</a>'
                    % (url_for(st["lang"], "state", st["slug"]), st["lang"],
                       st["lang"], esc(fmt(lang, "s_lang_btn", v))))

    lang_block = ""
    if st["lang"] != "en":
        lang_block = """
    <div class="callout" style="margin-top:36px">
      <h3 style="margin-top:0">{h2}</h3>
      <p>{p}</p>
      {swap}
    </div>""".format(h2=esc(fmt(lang, "s_lang_h2", v)),
                     p=esc(fmt(lang, "s_lang_p", v)), swap=swap)

    l4 = (fmt(lang, "s_local_l4", v) if other
          else STR[lang]["s_local_l4_en"])

    body = """
<section class="hero">
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="{home}">{bc_home}</a>
      <span aria-hidden="true">/</span>
      <a href="{p}/india">{bc_india}</a>
      <span aria-hidden="true">/</span>
      <span aria-current="page">{state}</span>
    </nav>
    <div class="wrap-narrow" style="padding:0">
      <span class="eyebrow">{eyebrow}</span>
      <h1 style="max-width:none">{h1}</h1>
      <p class="lede">{lede}</p>
      <div class="btn-row">
        <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta1}</a>
        <a class="btn btn-ghost btn-lg" href="{p}/workqueue">{cta2}</a>
      </div>
      {trust}
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap wrap-narrow">
    <div class="section-head">
      <h2>{where_h2}</h2>
      <p class="lede">{where_p}</p>
    </div>

    <h3 class="group-head">{cities_h}</h3>
    <div class="chip-row">{city_chips}</div>
    <p class="small muted" style="margin-top:14px">{cities_p}</p>
    {lang_block}
  </div>
</section>

<section class="band">
  <div class="wrap wrap-narrow">
    <div class="section-head">
      <h2>{local_h2}</h2>
    </div>
    {local_list}
  </div>
</section>

<section>
  <div class="wrap wrap-narrow center">
    <h2>{other_h2}</h2>
    <p class="lede">{other_p}</p>
    <a class="btn btn-ghost" href="{p}/india">{other_btn}</a>
  </div>
</section>

<section class="band cta-band">
  <div class="wrap">
    <h2>{cta_h2}</h2>
    <p class="lede">{cta_p}</p>
    <div class="btn-row center">
      <a class="btn btn-primary btn-lg" href="{p}/contact?about=trial">{cta_b1}</a>
      <a class="btn btn-ghost btn-lg" href="{p}/pricing">{cta_b2}</a>
    </div>
  </div>
</section>
""".format(home=(p + "/") if p else "/", p=p, bc_home=esc(s["s_bc_home"]),
           bc_india=esc(s["s_bc_india"]), state=esc(name),
           eyebrow=esc(name), h1=esc(fmt(lang, "s_h1", v)),
           lede=esc(fmt(lang, "s_lede", v)),
           cta1=esc(s["h_cta_b1"]), cta2=esc(s["h_cta1"]),
           trust=trust_row([s["h_trust1"], s["h_trust2"], s["w_trust1"]]),
           where_h2=esc(fmt(lang, "s_where_h2", v)),
           where_p=esc(fmt(lang, "s_where_p", v)),
           cities_h=esc(s["s_cities_h"]),
           city_chips="".join('<span class="chip chip-plain">%s</span>' % esc(c)
                              for c in cities),
           cities_p=esc(fmt(lang, "s_cities_p", v)), lang_block=lang_block,
           local_h2=esc(fmt(lang, "s_local_h2", v)),
           local_list=check_list([
               (s["s_local_l1_b"], fmt(lang, "s_local_l1", v)),
               (s["s_local_l2_b"], fmt(lang, "s_local_l2", v)),
               (s["s_local_l3_b"], fmt(lang, "s_local_l3", v)),
               (s["s_local_l4_b"], l4)]),
           other_h2=esc(s["s_other_h2"]), other_p=esc(s["s_other_p"]),
           other_btn=esc(s["s_other_btn"]),
           cta_h2=esc(fmt(lang, "s_cta_h2", v)),
           cta_p=esc(fmt(lang, "s_cta_p", v)),
           cta_b1=esc(s["h_cta_b1"]), cta_b2=esc(s["h_cta_b2"]))

    # Only the versions that really exist go in hreflang.
    alts = {"en": url_for("en", "state", st["slug"])}
    if st["lang"] != "en":
        alts[st["lang"]] = url_for(st["lang"], "state", st["slug"])

    # The picker still offers every language; the ones without a version of
    # this page land on their own India hub, which is the nearest true thing.
    targets = {}
    for l in LANGS:
        targets[l["code"]] = (alts[l["code"]] if l["code"] in alts
                              else url_for(l["code"], "india"))

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": fmt(lang, "s_title", v),
         "url": SITE + url_for(lang, "state", st["slug"]),
         "about": {"@type": "AdministrativeArea", "name": st["name"],
                   "identifier": st["iso"],
                   "containedInPlace": {"@type": "Country", "name": "India"}}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": s["s_bc_home"],
             "item": SITE + url_for(lang, "home")},
            {"@type": "ListItem", "position": 2, "name": s["s_bc_india"],
             "item": SITE + url_for(lang, "india")},
            {"@type": "ListItem", "position": 3, "name": name,
             "item": SITE + url_for(lang, "state", st["slug"])}]},
        dict(software_ld(lang),
             areaServed={"@type": "AdministrativeArea", "name": st["name"],
                         "identifier": st["iso"]})]}
    for node in ld["@graph"]:
        node.pop("@context", None)

    return (head(lang, state_title(lang, v), fmt(lang, "s_desc", v),
                 url_for(lang, "state", st["slug"]), alts, jsonld=ld,
                 geo=(st["iso"], st["name"]))
            + header(lang, "india", targets) + body + footer(lang))


# --- 5. The hand-written English pages --------------------------------------

MARKERS = ("hreflang", "langpicker", "jsonld")


def patch_english():
    """Replace what is between the <!-- qw:x --> markers in the four
    hand-written English pages. Everything outside them is left alone."""
    pages = [("home", "index.html"), ("workqueue", "workqueue.html"),
             ("pricing", "pricing.html"), ("contact", "contact.html")]
    for page, filename in pages:
        path = os.path.join(PUBLIC, filename)
        with io.open(path, encoding="utf-8") as f:
            html = f.read()

        blocks = {
            "hreflang": hreflang_block(core_alts(page)),
            "langpicker": lang_picker("en", core_targets(page)),
        }
        if page == "home":
            faqs = [(STR["en"]["h_faq_q%d" % i], STR["en"]["h_faq_a%d" % i])
                    for i in range(1, 6)]
            graph = [org_ld(), software_ld("en"),
                     {"@type": "WebSite", "name": "Quietworks", "url": SITE + "/",
                      "inLanguage": [l["hreflang"] for l in LANGS]},
                     faq_ld(faqs)]
        elif page == "workqueue":
            faqs = [(STR["en"]["w_faq_q%d" % i], STR["en"]["w_faq_a%d" % i])
                    for i in range(1, 7)]
            graph = [software_ld("en"), faq_ld(faqs)]
        elif page == "pricing":
            faqs = [(STR["en"]["p_faq_q%d" % i], STR["en"]["p_faq_a%d" % i])
                    for i in range(1, 6)]
            graph = [software_ld("en"), faq_ld(faqs)]
        else:
            graph = [org_ld()]
        for node in graph:
            node.pop("@context", None)
        blocks["jsonld"] = ('<script type="application/ld+json">%s</script>'
                            % json.dumps({"@context": "https://schema.org",
                                          "@graph": graph},
                                         ensure_ascii=False,
                                         separators=(",", ":")))

        for name, content in blocks.items():
            pattern = re.compile(r"(<!-- qw:%s -->).*?(<!-- /qw:%s -->)"
                                 % (name, name), re.S)
            if not pattern.search(html):
                sys.exit("public/%s has no <!-- qw:%s --> marker" % (filename, name))
            html = pattern.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(2),
                               html)

        written.append(filename)
        if CHECK:
            if io.open(path, encoding="utf-8").read() != html:
                stale.append(filename)
            continue
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)


# --- 6. Sitemap and robots --------------------------------------------------

def put(name, text):
    """Write (or, under --check, compare) a file straight in public/."""
    path = os.path.join(PUBLIC, name)
    if CHECK:
        current = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if current != text:
            stale.append(name)
    else:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    written.append(name)


def build_sitemap():
    """Every URL carries the hreflang set of the page it is - the same set the
    page's own <head> declares, so the two can never drift."""
    urls = []

    def add(loc, alts, priority, freq="monthly"):
        urls.append((loc, alts, priority, freq))

    for l in LANGS:
        code = l["code"]
        first = code == "en"
        add(url_for(code, "home"), core_alts("home"), "1.0" if first else "0.9")
        add(url_for(code, "workqueue"), core_alts("workqueue"), "0.9" if first else "0.8")
        add(url_for(code, "pricing"), core_alts("pricing"), "0.8" if first else "0.7")
        add(url_for(code, "india"), core_alts("india"), "0.8" if first else "0.7")
        add(url_for(code, "contact"), core_alts("contact"), "0.6", "yearly")

    for st in STATES:
        alts = {"en": url_for("en", "state", st["slug"])}
        if st["lang"] != "en":
            alts[st["lang"]] = url_for(st["lang"], "state", st["slug"])
        for href in alts.values():
            add(href, alts, "0.7")

    rows = []
    for loc, alts, priority, freq in urls:
        links = "\n".join(
            '    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>'
            % (BY_CODE[c]["hreflang"], SITE, href) for c, href in alts.items())
        rows.append("""  <url>
    <loc>%s%s</loc>
%s
    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>
    <lastmod>%s</lastmod>
    <changefreq>%s</changefreq>
    <priority>%s</priority>
  </url>""" % (SITE, loc, links, SITE, alts["en"], TODAY, freq, priority))

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    with io.open(os.path.join(PUBLIC, "sitemap.xml"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write(xml)
    written.append("sitemap.xml")
    return len(urls)


def build_robots():
    txt = """User-agent: *
Allow: /

# One page per state and per language; nothing here is a crawl trap.
Sitemap: %s/sitemap.xml
""" % SITE
    with io.open(os.path.join(PUBLIC, "robots.txt"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write(txt)
    written.append("robots.txt")


# --- 7. Run it --------------------------------------------------------------

def main():
    builders = {"home": build_home, "workqueue": build_workqueue,
                "pricing": build_pricing, "contact": build_contact}

    for l in LANGS:
        code = l["code"]
        if code != "en":
            for page, _ in CORE:
                write(url_for(code, page), builders[page](code))
        write(url_for(code, "india"), build_india(code))

    for st in STATES:
        write(url_for("en", "state", st["slug"]), build_state(st, "en"))
        if st["lang"] != "en":
            write(url_for(st["lang"], "state", st["slug"]),
                  build_state(st, st["lang"]))

    patch_english()
    n = build_sitemap()
    build_robots()

    if CHECK:
        if stale:
            print("%d files are out of date - run tools/build_i18n.py:" % len(stale))
            for name in stale[:20]:
                print("  ", name)
            sys.exit(1)
        print("%d generated files are up to date" % len(written))
        return
    print("%d files written under public/" % len(written))
    print("  %d languages, %d states, %d urls in the sitemap"
          % (len(LANGS), len(STATES), n))


if __name__ == "__main__":
    main()
