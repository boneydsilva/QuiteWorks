---
name: quietworks-site
description: Edit, preview, re-record or deploy the Quietworks marketing site (boneydsilva.com) - the plain HTML/CSS/JS site that sells WorkQueue. Use for any change to public/, the demo film, the screenshots, pricing or copy, and for "why is the video not seeking", "the page jumps", "deploy the site", or adding a page for a new tool.
---

# Quietworks site

`D:\BoneysNewWebsiteProcessAutoamation` — plain HTML, CSS and JS. **No build
step, no npm, no framework.** What is in `public/` is exactly what is served.
Live at <https://boneydsilva.com> on Cloudflare Workers static assets.

Deploy is `git add -A; git commit; git push` — Cloudflare rebuilds in about
40 seconds. Only `public/` is published; `tools/`, `deploy/` and the READMEs
stay private. The repo is `boneydsilva/QuiteWorks` (the name misspells the
brand; leave it).

## Preview

```powershell
python tools\preview.py          # http://localhost:8000
```

Always this, never `python -m http.server`: the site uses clean URLs
(`/workqueue`, not `/workqueue.html`) because that is what Cloudflare serves,
and `preview.py` applies the same rule, serves the real 404 page, and answers
Range requests so the demo film can be seeked locally.

## The shape of it

| | |
|---|---|
| Tokens for every colour, radius, width | top of `public/assets/css/site.css` |
| Email, WhatsApp number, form key | `SITE` block at the top of `public/assets/js/site.js` |
| CSS sections | numbered `/* --- 1. Tokens */` … keep them in order and renumber if you insert one |
| JS sections | numbered the same way, each an `initX()` called from one `DOMContentLoaded` |

Header, footer and nav are **copy-pasted into all five pages** — the cost of
having no build step. Change one, change all five, and `public/sitemap.xml`.
Once there are four or five tools that stops being tolerable; that is the
moment for a tiny build step or Astro, not before.

Dark mode lives in three blocks that must stay in step: `:root`,
`@media (prefers-color-scheme: dark) :root:not([data-theme="light"])`, and
`:root[data-theme="dark"]`.

## Rules the site holds itself to

- **No testimonials, customer counts or invented numbers.** There are no
  customers yet. Inventing one loses the first deal that asks for a reference.
- **Nothing that claims to be a capture unless it is one.** The film and the
  screenshots say plainly what they are, and where the names are invented.
- **No cookie banner, no analytics, no payment integration** — all deliberate.
  Plausible or Cloudflare Web Analytics need no banner if he ever wants numbers.
- Every screenshot needs real `alt` text and explicit `width`/`height`, or the
  page jumps while images load.

## The demo film

`public/assets/video/workqueue-demo.mp4` — 1:07, 1920x1080, ~7 MB, the second
section of the home page. Real footage of WorkQueue 4.0.1, not an animation.
Poster: `public/assets/img/demo-poster.jpg`.

Re-recording is three commands, documented step by step in
**`tools/README.md`** (seed → serve → `record_demo.py` → `compose_demo.py`).
What is worth knowing before you start:

- **It needs a real bar running on this PC.** The strip in the film is a
  genuine Windows AppBar. `record_demo.py` borrows it — names it Asha Rao,
  empties its queue — and **puts it back** at the end. If it dies half way,
  clear the name and delete the demo tasks from the Machines tab yourself.
- **Headless Chrome only manages ~2.6 fps** on the screencast. The recorder
  uses an ordinary window parked off-screen (`--window-position=-2400,0`
  plus the occlusion flags) which gives ~6 fps. Do not "fix" it back to
  headless.
- **The shot list is the top half of `compose_demo.py`** — one entry per shot
  naming the seconds of recording it plays, the camera (centre and width, in
  the dashboard's CSS pixels) at each end of the move, and the caption.
  Check framing with `python tools\compose_demo.py <dir> still 7 25 36 58`
  rather than sitting through a five minute render.
- **If you re-cut the film, update `FILM_CHAPTERS` in `site.js`** — five
  timestamps — or the chapter buttons seek to the wrong places.
- The music is synthesised from sine partials in `tools/score_demo.py`.
  Nothing sampled, nothing licensed. Keep it that way: no stock music.

### Cloudflare does not answer Range requests

Workers static assets return the **whole file** for a `Range:` request.
Verified at origin with `CF-Cache-Status: MISS`. A streamed `<video>` therefore
reports `seekable.end === 0` — the scrub bar does nothing and every chapter
button lands back at zero.

So `initFilm()` fetches the mp4 and plays a `blob:` URL, which seeks perfectly.
The cost is that playback starts after the download, which is why the button
counts the download in and why the encode is held near 7 MB (CRF 24). If the
site ever moves somewhere that honours Range, that whole dance can go.

Test it, do not assume:

```powershell
curl.exe -s -D - -H "Range: bytes=100-199" -o NUL https://boneydsilva.com/assets/video/workqueue-demo.mp4
# 206 + Content-Range = seekable; 200 + the full Content-Length = not
```

## Screenshots

Real captures of WorkQueue on seeded demo data — regenerate them rather than
editing the old ones. `tools/README.md` has the three steps. The employee strip
cannot be captured headlessly (it is a native AppBar): grab the **top 44 pixels
of the screen**, the band Windows reserves, which nothing can overlap. Anything
else grabbed from this screen is unreliable — the terminal renders above other
windows.

To let people open a screenshot full size, wrap the `.shot` in
`<a class="shot-zoom" href="…" data-zoom>`; `initZoom()` upgrades it to an
overlay and the link still works with JavaScript off.

## Before saying a change works

Load every page in headless Chrome over CDP and assert **zero console
messages** — `/`, `/workqueue`, `/pricing`, `/contact` and a 404. Then check
the thing you changed in both themes and at 390 / 760 / 1280 px.

Watch for **layout that changes height while the page is idle** — an animating
section that grows by a card pushes the page under the reader. Sample the
element's height over a full cycle and assert it is constant.

## Still open

- `formAccessKey` in `site.js` is still `PASTE-YOUR-…`. Until it is set, the
  contact form falls back to a `mailto:`. Free key from web3forms.com.
- The rest of the pre-launch checklist is the table in `README.md`.

**This repo is public.** Anything written here ships to GitHub, so keep
commercial thinking — pricing rationale, licensing gaps, deal notes — out of
it and in the conversation instead.
